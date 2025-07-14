import streamlit as st

def calculate_delay_line_length(fm, tau_us_per_km):
    """
    Calculate delay line length in meters.
    
    Args:
        fm (float): Modulation frequency in Hz.
        tau_us_per_km (float): Propagation delay in microseconds per kilometer.
    
    Returns:
        float: Length of the delay line in meters.
    """
    tau_s_per_km = tau_us_per_km * 1e-6  # Convert μs to seconds
    half_period = 1 / (2 * fm)  # Half-period in seconds
    length_km = half_period / tau_s_per_km  # Length in km
    length_m = length_km * 1000  # Convert km to meters
    return length_m


st.header('Калькулятор задержки')

st.caption('Требования для целей учета электроэнергии и РЗА в сетях HVDC:')
st.write('Частота SV потока `96000 Гц`')
st.write('Задержка (time delay, td), мкс  `5 µs` – `25 µs` – `100 µs`')


st.write('Длина линии задержки зависит от частоты модуляции согласно:')
st.latex(r'''
         l = \left(\frac{\frac{1}{2f_m}}{\tau}\right)
         ''')
st.caption('tau=5 мкс/км - время распространения света в среде')

st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.number_input('Распространения света, мкс/км', value=5, key='light_speed')

with col2:
    st.number_input('Обработки DSP, мкс', value=5, key='dsp_delay')

with col3:
    st.number_input('Прочие задержки, мкс', value=1, key='other_delay')

st.slider('Частота модуляции, кГц', 10, 2000, 64, 10, key='fmod')

delay_length = calculate_delay_line_length(st.session_state.fmod*1000, st.session_state.light_speed)
delay_length_time = 0.001*delay_length*st.session_state.light_speed
total_delay_time = delay_length_time + st.session_state.dsp_delay + st.session_state.other_delay

st.write(f'Длина линия задержки: `{delay_length:.1f} м`')
st.write(f'Задержка на распростаранение света: `{delay_length_time:.1f} мкс`')
st.write(f'Общая зарежка: `{total_delay_time:.1f} мкс`')
