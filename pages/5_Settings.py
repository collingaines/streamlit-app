import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

# Sample data
import pandas as pd
data = pd.DataFrame({
    "Column 1": [1, 2, 3, 4],
    "Column 2": ["A", "B", "C", "D"],
    "Column 3": [True, False, True, False]
})

# Build grid options
gb = GridOptionsBuilder.from_dataframe(data)
gb.configure_default_column(editable=True)
grid_options = gb.build()

# Render the AgGrid table within a container
with st.container():
    # Render AgGrid
    AgGrid(
        data,
        gridOptions=grid_options,
        height=400,  # Initial height
        fit_columns_on_grid_load=True,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        theme="streamlit"
    )

# Add CSS and JavaScript for full-screen functionality
st.markdown("""
    <style>
    .full-screen-container {
        position: relative;
    }
    .full-screen-btn {
        position: absolute;
        top: 10px;
        right: 10px;
        z-index: 1000;
        background-color: #007bff;
        color: white;
        border: none;
        padding: 8px 12px;
        border-radius: 4px;
        cursor: pointer;
    }
    .full-screen-btn:hover {
        background-color: #0056b3;
    }
    .full-screen {
        position: fixed !important;
        top: 0 !important;
        left: 0 !important;
        width: 100% !important;
        height: 100% !important;
        z-index: 9999 !important;
        background: white !important;
        padding: 10px;
        overflow: auto;
    }
    .ag-theme-streamlit {
        height: 90vh !important;
        width: 100% !important;
    }
    </style>
    <div class="full-screen-container" id="full-screen-container">
        <button class="full-screen-btn" id="toggle-fullscreen-btn">Toggle Full Screen</button>
    </div>
    """, unsafe_allow_html=True)

# Add JavaScript for toggling full-screen mode
st.markdown("""
    <script>
    document.addEventListener("DOMContentLoaded", function() {
        const btn = document.getElementById('toggle-fullscreen-btn');
        const container = document.querySelector('.stAgGrid');  // AgGrid container class
        let isFullScreen = false;

        btn.addEventListener('click', () => {
            if (!isFullScreen) {
                container.classList.add('full-screen');
                btn.innerText = 'Exit Full Screen';
                isFullScreen = true;
            } else {
                container.classList.remove('full-screen');
                btn.innerText = 'Toggle Full Screen';
                isFullScreen = false;
            }
        });
    });
    </script>
    """, unsafe_allow_html=True)
