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
    # Add a placeholder for the AgGrid table
    table_container = st.empty()

    # Render AgGrid
    AgGrid(
        data,
        gridOptions=grid_options,
        height=400,  # Set a fixed initial height
        fit_columns_on_grid_load=True,
        update_mode=GridUpdateMode.SELECTION_CHANGED,
        theme="streamlit"
    )

# Add the full-screen toggle button and container
st.markdown("""
    <style>
    #full-screen-container {
        position: relative;
        width: 100%;
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
        height: 90vh !important;  /* Full height in full-screen mode */
        width: 100% !important;   /* Full width in full-screen mode */
    }
    </style>
    <div id="full-screen-container">
        <button class="full-screen-btn" id="toggle-fullscreen-btn">Toggle Full Screen</button>
    </div>
    """, unsafe_allow_html=True)

# Add JavaScript for full-screen toggling
st.markdown("""
    <script>
    const btn = document.getElementById('toggle-fullscreen-btn');
    const container = document.getElementById('full-screen-container');
    const gridDiv = document.querySelector('.ag-theme-streamlit');

    let isFullScreen = false;

    btn.addEventListener('click', () => {
        if (!isFullScreen) {
            container.classList.add('full-screen');
            if (gridDiv) {
                gridDiv.style.height = "90vh";
                gridDiv.style.width = "100%";
            }
            btn.innerText = 'Exit Full Screen';
            isFullScreen = true;
        } else {
            container.classList.remove('full-screen');
            if (gridDiv) {
                gridDiv.style.height = "400px";
                gridDiv.style.width = "100%";
            }
            btn.innerText = 'Toggle Full Screen';
            isFullScreen = false;
        }
    });
    </script>
    """, unsafe_allow_html=True)
