import streamlit as st
import pandas as pd
from datetime import date, timedelta
from supabase_service import SupabaseService
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Streamlit Page Configuration (Must be the first Streamlit command) ---
st.set_page_config(layout="wide")


# --- Supabase Setup ---
@st.cache_resource  # Cache the service object itself
def get_supabase_service():
    """Initializes and returns the SupabaseService instance."""
    try:
        return SupabaseService()
    except ValueError as e:
        st.error(f"Failed to initialize Supabase connection: {e}")
        st.error(
            "Please ensure SUPABASE_URL and SUPABASE_KEY are set in your .env file."
        )
        return None
    except Exception as e:
        st.error(f"An unexpected error occurred during Supabase initialization: {e}")
        return None


supabase_service = get_supabase_service()


# --- Data Loading ---
@st.cache_data(ttl=600)  # Cache data for 10 minutes
def load_data(start_date=None, end_date=None):
    """Loads message data from Supabase within the specified date range."""
    if supabase_service is None:
        return pd.DataFrame()  # Return empty DataFrame if service failed

    start_date_str = start_date.isoformat() if start_date else None
    end_date_str = end_date.isoformat() if end_date else None

    try:
        data = supabase_service.get_messages_in_range(
            start_date=start_date_str, end_date=end_date_str
        )
        if not data:
            return pd.DataFrame()  # Return empty if no data fetched

        df = pd.DataFrame(data)
        # Convert timestamp to datetime objects (adjust based on actual format from Supabase)
        # Assuming Supabase returns ISO 8601 format strings
        df["timestamp"] = pd.to_datetime(df["timestamp"])
        # Ensure 'x' is numeric, coercing errors to NaN (which we'll handle)
        df["x"] = pd.to_numeric(df["x"], errors="coerce")
        # Ensure reply_to_message_id is integer
        df["reply_to_message_id"] = (
            pd.to_numeric(df["reply_to_message_id"], errors="coerce")
            .fillna(0)
            .astype(int)
        )

        return df
    except Exception as e:
        st.error(f"Error loading data from Supabase: {e}")
        return pd.DataFrame()


# --- Streamlit UI ---
st.title("📊 Message Analysis Dashboard")

if supabase_service is None:
    st.warning("Dashboard cannot function without a valid Supabase connection.")
else:
    # --- Sidebar Filters ---
    st.sidebar.header("Filters")
    # Use min/max dates or reasonable defaults if needed
    # Default to last 7 days
    today = date.today()
    default_start = today - timedelta(days=7)

    start_date_input = st.sidebar.date_input(
        "Start Date",
        value=None,
        help="Leave blank to include all data from the beginning.",
    )
    end_date_input = st.sidebar.date_input(
        "End Date", value=None, help="Leave blank to include all data up to today."
    )

    st.sidebar.divider()  # Add a visual separator

    # --- Additional Filters ---
    mc_filter_k = st.sidebar.number_input(
        "Marketcap (in thousands)",
        min_value=0,
        value=None,
        step=10,
        help="Filter by minimum marketcap (e.g., 100 = $100,000). Leave blank for no filter.",
    )
    vol_filter_k = st.sidebar.number_input(
        "Volume (in thousands)",
        min_value=0,
        value=None,
        step=10,
        help="Filter by minimum volume (e.g., 100 = $100,000). Leave blank for no filter.",
    )
    top_10_holder_filter = st.sidebar.number_input(
        "Top 10 Holder (%)",
        min_value=0.0,
        max_value=100.0,
        value=None,
        step=1.0,
        help="Filter by minimum Top 10 Holder percentage. Leave blank for no filter.",
    )
    x_filter = st.sidebar.number_input(
        "X Value",
        value=None,
        step=1.0,
        help="Filter by exact X value. Leave blank for no filter.",
    )
    dex_paid_filter = st.sidebar.checkbox("Dex Paid", value=False)

    # --- Load Data Based on Filters ---
    df_loaded = load_data(start_date=start_date_input, end_date=end_date_input)

    # --- Apply Additional Filters ---
    df_filtered = df_loaded.copy()  # Start with the date-filtered data

    if mc_filter_k is not None:
        mc_filter = mc_filter_k * 1000  # Convert thousands to actual value
        # Ensure 'mc' column exists and is numeric before filtering
        if "mc" in df_filtered.columns:
            df_filtered["mc"] = pd.to_numeric(df_filtered["mc"], errors="coerce")
            df_filtered = df_filtered[df_filtered["mc"] >= mc_filter]
        else:
            st.sidebar.warning("Marketcap (mc) column not found in data.")

    if vol_filter_k is not None:
        vol_filter = vol_filter_k * 1000  # Convert thousands to actual value
        # Ensure 'vol' column exists and is numeric before filtering
        if "vol" in df_filtered.columns:
            df_filtered["vol"] = pd.to_numeric(df_filtered["vol"], errors="coerce")
            df_filtered = df_filtered[df_filtered["vol"] >= vol_filter]
        else:
            st.sidebar.warning("Volume (vol) column not found in data.")

    if top_10_holder_filter is not None:
        # Ensure 'top_10_holder' column exists and is numeric before filtering
        if "top_10_holder" in df_filtered.columns:
            df_filtered["top_10_holder"] = pd.to_numeric(
                df_filtered["top_10_holder"], errors="coerce"
            )
            # Filter where the data's top_10_holder is >= the filter value
            df_filtered = df_filtered[
                df_filtered["top_10_holder"] >= top_10_holder_filter
            ]
        else:
            st.sidebar.warning(
                "Top 10 Holder (top_10_holder) column not found in data."
            )

    if x_filter is not None:
        # 'x' is already converted to numeric in load_data
        df_filtered = df_filtered[df_filtered["x"] == x_filter]

    if dex_paid_filter:
        # Ensure 'dex_paid' column exists and treat it as boolean
        if "dex_paid" in df_filtered.columns:
            # Convert potential different types to boolean (e.g., 0/1, True/False strings)
            df_filtered["dex_paid"] = df_filtered["dex_paid"].astype(bool)
            df_filtered = df_filtered[df_filtered["dex_paid"] == True]
        else:
            st.sidebar.warning("Dec Paid (dex_paid) column not found in data.")

    # --- Display Data ---
    if df_filtered.empty:
        st.warning(
            "No message data found for the selected period or an error occurred."
        )
    else:
        st.success(
            f"Loaded {len(df_loaded)} messages initially. Displaying {len(df_filtered)} after filtering."
        )

        # --- Create Tabs ---
        tab1, tab2 = st.tabs(["📊 Signal X Status", "📈 X Distribution"])

        # --- Tab 1: Signal X Status Analysis ---
        with tab1:
            st.header("Signal 'X' Status")

            # Filter for signals (original messages, not replies) using the *filtered* dataframe
            signals_df = df_filtered[
                df_filtered["reply_to_message_id"] == 0
            ].copy()  # Use .copy() to avoid SettingWithCopyWarning

            total_signals = len(signals_df)

            if total_signals == 0:
                st.info("No signals found in the selected period.")
            else:
                # Count signals still needing an update (x == -1)
                # Handle potential NaN values from coercion if 'x' was invalid
                signals_no_x = signals_df[signals_df["x"].fillna(-1) == -1]
                count_no_x = len(signals_no_x)

                # Count signals that have received an update (x > 0)
                signals_with_x = signals_df[signals_df["x"].fillna(-1) > 0]
                count_with_x = len(signals_with_x)

                # Calculate percentages
                percent_no_x = (
                    (count_no_x / total_signals) * 100 if total_signals > 0 else 0
                )
                percent_with_x = (
                    (count_with_x / total_signals) * 100 if total_signals > 0 else 0
                )

                # Display Metrics
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Signals", f"{total_signals:,}")
                col2.metric(
                    "Signals without X Update",
                    f"{count_no_x:,}",
                    f"{percent_no_x:.1f}% of total",
                )
                col3.metric(
                    "Signals with X Update",
                    f"{count_with_x:,}",
                    f"{percent_with_x:.1f}% of total",
                )

        # --- Tab 2: X Distribution Chart ---
        with tab2:
            st.header("Distribution of 'X' Values for Updated Signals")

            # Filter signals that have an update (x > 0, excluding -1)
            updated_signals = signals_df[signals_df["x"] > 0].copy()

            if updated_signals.empty:
                st.info(
                    "No signals with an X update (> 0) found in the selected period."
                )
            else:
                # Count signals per x value
                x_distribution = updated_signals["x"].value_counts().sort_index()

                # Rename index for clarity in the chart
                x_distribution.index.name = "X Value"
                x_distribution = x_distribution.reset_index()
                x_distribution.columns = ["X Value", "Number of Signals"]

                # Display the bar chart
                st.bar_chart(x_distribution, x="X Value", y="Number of Signals")
