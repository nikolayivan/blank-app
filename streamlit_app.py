import streamlit as st
import math
import pandas as pd

def calculate_delay_line_length(fm, tau_us_per_km, n_period=0):
    """
    Рассчитать длину линии задержки в метрах для рефлективного оптического пути.
    
    Args:
        fm (float): Частота модуляции в Гц.
        tau_us_per_km (float): Задержка распространения в микросекундах на километр.
        n_period (int): Множитель периода (0.5+N, N=0, 1, 2, ...).
    
    Returns:
        float: Длина линии задержки в метрах (без учета фиксированных компонентов).
    """
    tau_s_per_km = tau_us_per_km * 1e-6  # Конвертация мкс в секунды
    quarter_period = 1 / (4 * fm)  # Четверть периода с учетом N
    length_km = quarter_period / tau_s_per_km  # Длина в км
    length_m = length_km * 1000  # Конвертация км в метры
    return length_m

def calculate_lpf_delay(fm, lpf_order=1, cutoff_factor=0.25):
    """
    Рассчитать групповую задержку низкочастотного фильтра (НЧФ).
    
    Args:
        fm (float): Частота модуляции в Гц.
        lpf_order (int): Порядок НЧФ (по умолчанию: 1).
        cutoff_factor (float): Отношение частоты среза к частоте модуляции (по умолчанию: 0.25).
    
    Returns:
        float: Групповая задержка НЧФ в микросекундах.
    """
    fc = fm * cutoff_factor  # Частота среза
    if lpf_order == 1:
        delay_s = 1 / (2 * math.pi * fc)  # Групповая задержка для НЧФ первого порядка
    else:
        delay_s = lpf_order / (2 * math.pi * fc)  # Приблизительно для высших порядков
    return delay_s * 1e6  # Конвертация в микросекунды

def calculate_phase_detector_delay(fm, num_samples=3):
    """
    Рассчитать задержку фазового детектора (ПЛИС).
    
    Args:
        fm (float): Частота модуляции в Гц.
        num_samples (int): Количество отсчетов для фильтрации гармоник (по умолчанию: 3).
    
    Returns:
        float: Задержка фазового детектора в микросекундах.
    """
    period_s = 1 / fm  # Один период модуляции
    harmonic_extraction_delay = period_s  # Задержка для выделения первой гармоники
    filtering_delay = num_samples * period_s  # Задержка для фильтрации гармоник
    return (harmonic_extraction_delay + filtering_delay) * 1e6  # Конвертация в микросекунды

st.header('Калькулятор задержки ОТТ')

st.subheader('IEC 61869-14:2018, IEC 61850, IEC 61869-9')
st.write('**Частота потока SV**: `96 кГц`')
st.write('**Общая задержка (td)**: `5–25 мкс` (учет электроэнергии), `≤100 мкс` (релейная защита)')
st.write('**Рекомендуемая частота модуляции**: `576–768 кГц` (3–4 × частота Найквиста для `96 кГц`)')

st.subheader('Расчет длины линии задержки')
st.latex(r'''
         l = \frac{\frac{1}{4f_m}}{\tau}
         ''')
st.caption('Где: l = длина линии задержки (км), fm = частота модуляции (Гц), τ = задержка распространения (с/км), N = множитель периода (0, 1, 2, ...)')

st.divider()
st.subheader('Входные параметры')
col1, col2, col3 = st.columns(3)
with col1:
    tau_us_per_km = st.number_input('Скорость света (мкс/км)', value=5.0, min_value=1.0, max_value=10.0, step=0.1, key='light_speed')
with col2:
    electro_optical_length = st.number_input('Длина в ЭОБ (м)', value=20.0, min_value=0.0, max_value=50.0, step=1.0, key='electro_optical')
with col3:
    connecting_cable_length = st.number_input('Длина кабеля + ЧЭ (м)', value=50.0, min_value=0.0, max_value=100.0, step=1.0, key='cable_length')

col1, col2, col3 = st.columns(3)
with col1:
    n_period = st.number_input('Множитель периода (N)', value=0, min_value=0, max_value=5, step=1, key='n_period')

col1, col2, col3 = st.columns(3)
with col1:
    dsp_delay = st.number_input('Задержка обработки DSP (мкс)', value=5.0, min_value=0.0, step=0.1, key='dsp_delay')
with col2:
    other_delay = st.number_input('Прочие задержки (мкс)', value=1.0, min_value=0.0, step=0.1, key='other_delay')
with col3:
    lpf_order = st.number_input('Порядок НЧФ', value=1, min_value=1, max_value=4, step=1, key='lpf_order')

col1, col2, col3 = st.columns(3)
with col1:
    num_samples = st.number_input('Количество отсчетов для фильтра гармоник', value=3, min_value=3, max_value=10, step=1, key='num_samples')

fmod_khz = st.slider('Частота модуляции (кГц)', 100, 2000, 576, 10, key='fmod', help='Рекомендуется: 576–768 кГц для потока SV 96 кГц')

# Расчеты
fmod = fmod_khz * 1000  # Конвертация кГц в Гц
delay_line_length = calculate_delay_line_length(fmod, tau_us_per_km, n_period)
total_optical_length = delay_line_length + electro_optical_length + connecting_cable_length
optical_delay = 2 * 0.001 * total_optical_length * tau_us_per_km  # Рефлективный путь: свет проходит дважды
lpf_delay = calculate_lpf_delay(fmod, lpf_order=lpf_order, cutoff_factor=0.25)
phase_detector_delay = calculate_phase_detector_delay(fmod, num_samples=num_samples)
data_transfer_delay = 0.5  # Фиксированная задержка передачи данных от ПЛИС к DSP
total_delay_time = optical_delay + lpf_delay + phase_detector_delay + dsp_delay + other_delay + data_transfer_delay

chart_data = pd.DataFrame(
    {
        "index": ['Delay']*6,
        'name': ['Оптика', 'НЧФ', 'ПЛИС', 'Передача данных', 'DSP', 'Прочие'],
        'values': [optical_delay, lpf_delay, phase_detector_delay, data_transfer_delay, dsp_delay, other_delay],
    }
)

st.subheader('Результаты')
# Отображение результатов
st.bar_chart(
    chart_data,
    x = "index",
    y = "values",
    color='name',
    horizontal = True
)

st.caption(f'**Длина линии задержки (переменная)**: `{delay_line_length:.1f} м`')
st.caption(f'**Общая длина оптического пути (линия задержки + электрооптический блок + кабель)**: `{total_optical_length:.1f} м`')
st.caption(f'**Задержка распространения света (рефлективный путь)**: `{optical_delay:.1f} мкс`')
st.caption(f'**Групповая задержка НЧФ**: `{lpf_delay:.1f} мкс`')
st.caption(f'**Задержка фазового детектора (ПЛИС)**: `{phase_detector_delay:.1f} мкс`')
st.caption(f'**Задержка передачи данных (ПЛИС к DSP)**: `{data_transfer_delay:.1f} мкс`')
st.caption(f'**Общая задержка**: `{total_delay_time:.1f} мкс`')

# Проверка требований к задержке
if 5 <= total_delay_time <= 25:
    st.success('Общая задержка соответствует требованиям учета электроэнергии (5–25 мкс).')
elif 25 < total_delay_time <= 100:
    st.warning('Общая задержка соответствует требованиям релейной защиты (≤100 мкс), но превышает требования учета.')
else:
    st.error('Общая задержка превышает требования релейной защиты (>100 мкс).')

# Проверка частоты модуляции для потока SV
if fmod >= 576000:  # 3 × частота Найквиста для 96 кГц
    st.success('Частота модуляции поддерживает поток SV 96 кГц (≥576 кГц).')
else:
    st.error('Частота модуляции слишком низкая для потока SV 96 кГц (требуется ≥576 кГц).')

# Проверка частоты дискретизации АЦП/ПЛИС
if fmod * 400 <= 1e9:  # Предполагаемый предел 1 ГГц для АЦП/ПЛИС
    st.success(f'АЦП/ПЛИС поддерживает требуемую частоту дискретизации ({fmod*400/1e6:.1f} МГц ≤ 1 ГГц).')
else:
    st.error(f'Частота дискретизации АЦП/ПЛИС ({fmod*400/1e6:.1f} МГц) превышает типичный предел 1 ГГц.')

# Предупреждение о шуме для N > 0
if n_period > 0:
    st.warning(f'Множитель периода N={n_period} увеличивает шум из-за большей длины оптического пути.')
