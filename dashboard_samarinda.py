import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="Dashboard Kependudukan Samarinda 2022-2024",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ===== LOAD DATA =====
@st.cache_data
def load_data():
    """Load data from Excel file"""
    try:
        # Try production path first (root folder)
        try:
            df = pd.read_excel('DATA PROJECT.xlsx')
        except FileNotFoundError:
            # Fallback to local development path
            df = pd.read_excel('data/DATA PROJECT.xlsx')
        
        df.columns = df.columns.str.lower().str.strip()
        
        df['tahun'] = df['tahun'].astype(str)
        df['kecamatan'] = df['kecamatan'].str.strip().str.title()
        df['kelurahan'] = df['kelurahan'].str.strip().str.title()
        df['kelamin'] = df['kelamin'].str.strip().str.upper()
        df['umur'] = pd.to_numeric(df['umur'], errors='coerce')
        df['jumlah'] = pd.to_numeric(df['jumlah'], errors='coerce')
        
        # Remove rows with missing values
        df = df.dropna()
        
        # STANDARDIZE: Convert umur >= 75 to 75
        df.loc[df['umur'] >= 75, 'umur'] = 75
        
        # Aggregate data after standardization (karena banyak row umur yang jadi 75)
        df = df.groupby(['tahun', 'kecamatan', 'kelurahan', 'kelamin', 'umur'], as_index=False)['jumlah'].sum()
        
        return df
    except Exception as e:
        st.error(f"Error loading data: {e}")
        st.info("Pastikan file 'DATA PROJECT.xlsx' ada di folder yang sama dengan dashboard_samarinda.py")
        return None
    
def format_number(num):
    """Format number with thousand separator"""
    return f"{num:,.0f}"

def create_population_pyramid(df_filtered):
    """Create population pyramid chart with age groups"""
    # Create age groups
    df_pyramid = df_filtered.copy()
    
    # Define age groups (updated untuk data yang sudah standardized ke 75+)
    bins = [0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 150]
    labels = ['0-4', '5-9', '10-14', '15-19', '20-24', '25-29', '30-34', '35-39', 
              '40-44', '45-49', '50-54', '55-59', '60-64', '65-69', '70-74', '75+']
    
    df_pyramid['age_group'] = pd.cut(df_pyramid['umur'], bins=bins, labels=labels, right=False)
    
    # Aggregate by age group and gender
    pyramid_data = df_pyramid.groupby(['age_group', 'kelamin'])['jumlah'].sum().reset_index()
    
    # Separate male and female
    male_data = pyramid_data[pyramid_data['kelamin'] == 'L'].copy()
    female_data = pyramid_data[pyramid_data['kelamin'] == 'P'].copy()
    
    # Ensure all age groups are present
    all_groups = pd.DataFrame({'age_group': labels})
    male_data = all_groups.merge(male_data, on='age_group', how='left').fillna(0)
    female_data = all_groups.merge(female_data, on='age_group', how='left').fillna(0)
    
    # Make male values negative for left side
    male_data['jumlah_display'] = -male_data['jumlah']
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=male_data['age_group'],
        x=male_data['jumlah_display'],
        name='Male',
        orientation='h',
        marker=dict(color='#3498db'),
        text=male_data['jumlah'].apply(lambda x: f'{x:,.0f}' if x > 0 else ''),
        textposition='inside',
        hovertemplate='<b>%{y}</b><br>Male: %{customdata:,.0f}<extra></extra>',
        customdata=male_data['jumlah']
    ))
    
    fig.add_trace(go.Bar(
        y=female_data['age_group'],
        x=female_data['jumlah'],
        name='Female',
        orientation='h',
        marker=dict(color='#e91e63'),
        text=female_data['jumlah'].apply(lambda x: f'{x:,.0f}' if x > 0 else ''),
        textposition='inside',
        hovertemplate='<b>%{y}</b><br>Female: %{x:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='Population Pyramid by Age Group and Gender',
        barmode='relative',
        height=600,
        xaxis=dict(
            title='Population',
            tickformat=',d',
            tickvals=[-40000, -30000, -20000, -10000, 0, 10000, 20000, 30000, 40000],
            ticktext=['40K', '30K', '20K', '10K', '0', '10K', '20K', '30K', '40K']
        ),
        yaxis=dict(
            title='Age Group',
            # Normal order: 0-4 di bawah, 75+ di atas
            categoryorder='array',
            categoryarray=labels  # Tidak di-reverse
        ),
        hovermode='y unified',
        showlegend=True,
        bargap=0.1
    )
    
    return fig

def create_kecamatan_bar_chart(df_filtered):
    """Create bar chart by kecamatan"""
    kec_data = df_filtered.groupby(['kecamatan', 'kelamin'])['jumlah'].sum().reset_index()
    kec_pivot = kec_data.pivot(index='kecamatan', columns='kelamin', values='jumlah').fillna(0)
    kec_pivot['total'] = kec_pivot.sum(axis=1)
    kec_pivot = kec_pivot.sort_values('total', ascending=True)
    
    fig = go.Figure()
    
    if 'L' in kec_pivot.columns:
        fig.add_trace(go.Bar(
            y=kec_pivot.index,
            x=kec_pivot['L'],
            name='Laki-laki',
            orientation='h',
            marker=dict(color='#3498db'),
            hovertemplate='<b>%{y}</b><br>Laki-laki: %{x:,.0f}<extra></extra>'
        ))
    
    if 'P' in kec_pivot.columns:
        fig.add_trace(go.Bar(
            y=kec_pivot.index,
            x=kec_pivot['P'],
            name='Perempuan',
            orientation='h',
            marker=dict(color='#e74c3c'),
            hovertemplate='<b>%{y}</b><br>Perempuan: %{x:,.0f}<extra></extra>'
        ))
    
    fig.update_layout(
        title='Jumlah Penduduk Per Kecamatan',
        barmode='stack',
        height=500,
        xaxis=dict(title='Jumlah Penduduk'),
        yaxis=dict(title='Kecamatan'),
        hovermode='y unified'
    )
    
    return fig

def create_kelurahan_bar_chart(df_filtered, top_n=15):
    """Create bar chart by kelurahan (top N)"""
    kel_data = df_filtered.groupby(['kelurahan', 'kelamin'])['jumlah'].sum().reset_index()
    kel_pivot = kel_data.pivot(index='kelurahan', columns='kelamin', values='jumlah').fillna(0)
    kel_pivot['total'] = kel_pivot.sum(axis=1)
    kel_pivot = kel_pivot.sort_values('total', ascending=False).head(top_n)
    kel_pivot = kel_pivot.sort_values('total', ascending=True)
    
    fig = go.Figure()
    
    if 'L' in kel_pivot.columns:
        fig.add_trace(go.Bar(
            y=kel_pivot.index,
            x=kel_pivot['L'],
            name='Laki-laki',
            orientation='h',
            marker=dict(color='#3498db')
        ))
    
    if 'P' in kel_pivot.columns:
        fig.add_trace(go.Bar(
            y=kel_pivot.index,
            x=kel_pivot['P'],
            name='Perempuan',
            orientation='h',
            marker=dict(color='#e74c3c')
        ))
    
    fig.update_layout(
        title=f'Top {top_n} Kelurahan dengan Populasi Terbesar',
        barmode='stack',
        height=600,
        xaxis=dict(title='Jumlah Penduduk'),
        yaxis=dict(title='Kelurahan')
    )
    
    return fig

def create_gender_pie_chart(df_filtered):
    """Create pie chart for gender distribution"""
    gender_data = df_filtered.groupby('kelamin')['jumlah'].sum()
    
    labels = ['Laki-laki' if k == 'L' else 'Perempuan' for k in gender_data.index]
    values = gender_data.values
    colors = ['#3498db' if k == 'L' else '#e74c3c' for k in gender_data.index]
    
    fig = go.Figure(data=[go.Pie(
        labels=labels,
        values=values,
        hole=0.4,
        marker=dict(colors=colors),
        textinfo='label+percent',
        hovertemplate='<b>%{label}</b><br>Jumlah: %{value:,.0f}<extra></extra>'
    )])
    
    fig.update_layout(
        title='Perbandingan Jenis Kelamin',
        height=400  
    )
    
    return fig

def create_year_trend_chart(df):
    """Create population trend chart across years - TANPA LINE TOTAL"""
    yearly_data = df.groupby(['tahun', 'kelamin'])['jumlah'].sum().reset_index()
    
    yearly_pivot = yearly_data.pivot(index='tahun', columns='kelamin', values='jumlah').reset_index()
    yearly_pivot = yearly_pivot.sort_values('tahun')
    
    fig = go.Figure()
    
    if 'L' in yearly_pivot.columns:
        fig.add_trace(go.Scatter(
            x=yearly_pivot['tahun'],
            y=yearly_pivot['L'],
            mode='lines+markers+text',
            name='Laki-laki',
            line=dict(color='#3498db', width=3),
            marker=dict(size=10),
            text=yearly_pivot['L'].apply(lambda x: f'{x:,.0f}'),
            textposition='top center',
            hovertemplate='<b>%{x}</b><br>Laki-laki: %{y:,.0f}<extra></extra>'
        ))
    
    if 'P' in yearly_pivot.columns:
        fig.add_trace(go.Scatter(
            x=yearly_pivot['tahun'],
            y=yearly_pivot['P'],
            mode='lines+markers+text',
            name='Perempuan',
            line=dict(color='#e91e63', width=3),
            marker=dict(size=10),
            text=yearly_pivot['P'].apply(lambda x: f'{x:,.0f}'),
            textposition='bottom center',
            hovertemplate='<b>%{x}</b><br>Perempuan: %{y:,.0f}<extra></extra>'
        ))
    
    # HAPUS TOTAL LINE (sesuai request user)
    
    fig.update_layout(
        title='Trend Pertumbuhan Penduduk Per Tahun',
        height=500,
        xaxis=dict(title='Tahun', type='category'),
        yaxis=dict(title='Jumlah Penduduk', tickformat=',d'),
        hovermode='x unified',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def main():
    df = load_data()
    
    if df is None:
        st.error("❌ Gagal memuat data!")
        st.info("Pastikan file 'DATA PROJECT.xlsx' ada di folder 'data/'")
        st.stop()
    
    st.title("📊 Dashboard Kependudukan Kota Samarinda")
    st.markdown("**Analisis Data Penduduk Tahun 2022-2024**")
    st.markdown("---")
    
    st.sidebar.header("⚙️ Pengaturan Dashboard")
    
    dashboard_mode = st.sidebar.radio(
        "Mode Analisis:",
        ["Analisis Single Tahun", "Perbandingan Multi Tahun"]
    )
    
    st.sidebar.markdown("---")
    
    if dashboard_mode == "Analisis Single Tahun":
        st.sidebar.subheader("📅 Pilih Tahun")
        available_years = sorted(df['tahun'].unique(), reverse=True)
        selected_year = st.sidebar.selectbox("Tahun:", available_years)
        
        df_year = df[df['tahun'] == selected_year].copy()
        
        st.markdown(f"### 📊 Data Tahun **{selected_year}**")
        st.markdown("---")
        
        st.sidebar.subheader("🗺️ Filter Wilayah")
        
        st.sidebar.info("🏙️ **Kota:** Samarinda")
        
        # Kecamatan filter - selectbox
        all_kecamatan = ['Semua Kecamatan'] + sorted(df_year['kecamatan'].unique())
        selected_kecamatan = st.sidebar.selectbox(
            "🏘️ Pilih Kecamatan:",
            options=all_kecamatan,
            index=0
        )
        
        # Filter df based on kecamatan
        if selected_kecamatan != 'Semua Kecamatan':
            df_filtered = df_year[df_year['kecamatan'] == selected_kecamatan].copy()
        else:
            df_filtered = df_year.copy()
        
        # Kelurahan filter (based on selected kecamatan)
        available_kelurahan = ['Semua Kelurahan'] + sorted(df_filtered['kelurahan'].unique())
        selected_kelurahan = st.sidebar.selectbox(
            "🏡 Pilih Kelurahan:",
            options=available_kelurahan,
            index=0
        )
        
        # Final filter
        if selected_kelurahan != 'Semua Kelurahan':
            df_filtered = df_filtered[df_filtered['kelurahan'] == selected_kelurahan].copy()
        
        # Age range filter - HARDCODE MAX KE 75
        st.sidebar.markdown("---")
        st.sidebar.subheader("👶👴 Filter Umur")
        
        min_age = 0  # Hardcode min
        max_age = 75  # Hardcode max ke 75
        
        age_range = st.sidebar.slider(
            "Range Umur:",
            min_value=min_age,
            max_value=max_age,
            value=(min_age, max_age),
            format="%d"
        )
        
        # Display caption
        st.sidebar.caption(f"Range terpilih: {age_range[0]} - 75+ tahun")
        
        # Apply age filter TERAKHIR
        df_filtered = df_filtered[
            (df_filtered['umur'] >= age_range[0]) & 
            (df_filtered['umur'] <= age_range[1])
        ].copy()
        
        # ===== METRICS BARU - LEBIH INSIGHTFUL =====
        st.header("📊 Ringkasan Data")
        
        # Calculate metrics
        total_pop = df_filtered['jumlah'].sum()
        
        # Pertumbuhan penduduk (vs tahun sebelumnya)
        prev_year = str(int(selected_year) - 1)
        if prev_year in df['tahun'].values:
            df_prev = df[df['tahun'] == prev_year]
            total_prev = df_prev['jumlah'].sum()
            growth = total_pop - total_prev
            growth_pct = (growth / total_prev * 100) if total_prev > 0 else 0
        else:
            growth = 0
            growth_pct = 0
        
        # Usia produktif (15-64 tahun)
        df_produktif = df_filtered[(df_filtered['umur'] >= 15) & (df_filtered['umur'] <= 64)]
        usia_produktif = df_produktif['jumlah'].sum()
        pct_produktif = (usia_produktif / total_pop * 100) if total_pop > 0 else 0
        
        # Rasio dependensi: (anak 0-14 + lansia 65+) / produktif * 100
        df_anak = df_filtered[df_filtered['umur'] < 15]
        df_lansia = df_filtered[df_filtered['umur'] >= 65]
        dependents = df_anak['jumlah'].sum() + df_lansia['jumlah'].sum()
        rasio_dependensi = (dependents / usia_produktif * 100) if usia_produktif > 0 else 0
        
        # Kecamatan terbesar
        kec_largest = df_filtered.groupby('kecamatan')['jumlah'].sum().idxmax()
        kec_largest_pop = df_filtered.groupby('kecamatan')['jumlah'].sum().max()
        
        # Display metrics dengan mini charts
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric(
                "👥 Total Penduduk",
                format_number(total_pop)
            )
            # Mini sparkline untuk trend total (3 tahun terakhir)
            years_trend = sorted([y for y in df['tahun'].unique()])[-3:]
            trend_data = [df[df['tahun'] == y]['jumlah'].sum() for y in years_trend]
            
            fig_spark1 = go.Figure()
            fig_spark1.add_trace(go.Scatter(
                x=years_trend,
                y=trend_data,
                mode='lines',
                line=dict(color='#3498db', width=2),
                fill='tozeroy',
                fillcolor='rgba(52, 152, 219, 0.2)'
            ))
            fig_spark1.update_layout(
                height=80,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_spark1, use_container_width=True, config={'displayModeBar': False})
        
        with col2:
            if selected_year != '2022':
                st.metric(
                    "📈 Pertumbuhan",
                    f"{growth_pct:+.2f}%",
                    delta=f"{growth:+,} jiwa"
                )
            else:
                st.metric(
                    "📈 Pertumbuhan",
                    "N/A",
                )
                st.caption("Data tahun sebelumnya tidak tersedia")
            
            # Mini bar chart untuk growth
            if selected_year != '2022':
                fig_spark2 = go.Figure()
                fig_spark2.add_trace(go.Bar(
                    x=['2022', '2023', '2024'][:int(selected_year)-2021],
                    y=[0, 1.43, 2.25][:int(selected_year)-2021] if selected_year != '2022' else [0],
                    marker=dict(color=['#e74c3c' if x < 0 else '#2ecc71' for x in [0, 1.43, 2.25][:int(selected_year)-2021]])
                ))
                fig_spark2.update_layout(
                    height=80,
                    margin=dict(l=0, r=0, t=0, b=0),
                    xaxis=dict(visible=False),
                    yaxis=dict(visible=False),
                    showlegend=False,
                    plot_bgcolor='rgba(0,0,0,0)',
                    paper_bgcolor='rgba(0,0,0,0)'
                )
                st.plotly_chart(fig_spark2, use_container_width=True, config={'displayModeBar': False})
        
        with col3:
            st.metric(
                "💼 Usia Produktif",
                format_number(usia_produktif)
            )
            st.caption(f"{pct_produktif:.1f}% dari total")
            
            # Mini donut chart
            fig_spark3 = go.Figure()
            fig_spark3.add_trace(go.Pie(
                values=[usia_produktif, total_pop - usia_produktif],
                hole=0.6,
                marker=dict(colors=['#3498db', '#ecf0f1']),
                textinfo='none',
                hoverinfo='skip'
            ))
            fig_spark3.update_layout(
                height=80,
                margin=dict(l=0, r=0, t=0, b=0),
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_spark3, use_container_width=True, config={'displayModeBar': False})
        
        with col4:
            st.metric(
                "👶👴 Rasio Dependensi",
                f"{rasio_dependensi:.1f}",
            )
            st.caption("per 100 produktif")
            
            # Mini gauge chart
            fig_spark4 = go.Figure()
            fig_spark4.add_trace(go.Indicator(
                mode="gauge",  # Hilangkan "+number" agar angka tidak muncul
                value=rasio_dependensi,
                domain={'x': [0, 1], 'y': [0, 1]},
                gauge={
                    'axis': {'range': [None, 100], 'visible': False},
                    'bar': {'color': "#e74c3c" if rasio_dependensi > 50 else "#f39c12" if rasio_dependensi > 40 else "#2ecc71"},
                    'bgcolor': "rgba(0,0,0,0)",
                    'borderwidth': 0,
                }
            ))
            fig_spark4.update_layout(
                height=60,
                margin=dict(l=0, r=0, t=0, b=0),
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_spark4, use_container_width=True, config={'displayModeBar': False})
        
        with col5:
            st.metric(
                "🏘️ Kecamatan Terbesar",
                kec_largest[:12] + "..." if len(kec_largest) > 12 else kec_largest,
            )
            st.caption(f"{format_number(kec_largest_pop)} jiwa")
            
            # Mini bar chart top 3 kecamatan
            top3_kec = df_filtered.groupby('kecamatan')['jumlah'].sum().nlargest(3)
            fig_spark5 = go.Figure()
            fig_spark5.add_trace(go.Bar(
                x=top3_kec.values,
                y=[k[:10] for k in top3_kec.index],
                orientation='h',
                marker=dict(color='#3498db')
            ))
            fig_spark5.update_layout(
                height=80,
                margin=dict(l=0, r=0, t=0, b=0),
                xaxis=dict(visible=False),
                yaxis=dict(visible=False),
                showlegend=False,
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)'
            )
            st.plotly_chart(fig_spark5, use_container_width=True, config={'displayModeBar': False})
        
        # Sex ratio info box (tidak di metrics utama, tapi tetap ada)
        if total_pop > 0:
            total_male = df_filtered[df_filtered['kelamin'] == 'L']['jumlah'].sum()
            total_female = df_filtered[df_filtered['kelamin'] == 'P']['jumlah'].sum()
            if total_female > 0:
                sex_ratio = (total_male / total_female * 100)
                st.info(f"**Rasio Jenis Kelamin:** {sex_ratio:.2f} laki-laki per 100 perempuan")
        
        st.markdown("---")
        
        # Population Trend
        st.header("📈 Trend Pertumbuhan Penduduk")
        st.markdown("*Pertumbuhan populasi dari tahun ke tahun*")
        fig_trend = create_year_trend_chart(df)
        st.plotly_chart(fig_trend, use_container_width=True)
        
        st.markdown("---")
        
        # Piramida Penduduk
        st.header("👥 Piramida Penduduk")
        fig_pyramid = create_population_pyramid(df_filtered)
        st.plotly_chart(fig_pyramid, use_container_width=True)
        
        st.markdown("---")
        
        # Kecamatan and Gender
        col_left, col_right = st.columns([2, 1])
        
        with col_left:
            st.header("🏘️ Analisis Per Kecamatan")
            fig_kec = create_kecamatan_bar_chart(df_filtered)
            st.plotly_chart(fig_kec, use_container_width=True)
        
        with col_right:
            st.header("⚧️ Distribusi Gender")
            fig_gender = create_gender_pie_chart(df_filtered)
            st.plotly_chart(fig_gender, use_container_width=True)
        
        st.markdown("---")
        
        st.header("🏡 Analisis Per Kelurahan")
        top_n = st.slider("Tampilkan Top N Kelurahan:", 10, 30, 15)
        fig_kel = create_kelurahan_bar_chart(df_filtered, top_n)
        st.plotly_chart(fig_kel, use_container_width=True)
        
        st.markdown("---")
        
        # HAPUS CHART DISTRIBUSI UMUR (redundant dengan piramida)
        
        st.header("📋 Tabel Data Detail")
        
        tab1, tab2, tab3 = st.tabs(["Per Kecamatan", "Per Kelurahan", "Data Mentah"])
        
        with tab1:
            summary_kec = df_filtered.groupby('kecamatan').agg({
                'jumlah': 'sum'
            }).reset_index().sort_values('jumlah', ascending=False)
            summary_kec.columns = ['Kecamatan', 'Total Penduduk']
            st.dataframe(summary_kec, use_container_width=True, hide_index=True)
        
        with tab2:
            summary_kel = df_filtered.groupby(['kecamatan', 'kelurahan']).agg({
                'jumlah': 'sum'
            }).reset_index().sort_values('jumlah', ascending=False)
            summary_kel.columns = ['Kecamatan', 'Kelurahan', 'Total Penduduk']
            st.dataframe(summary_kel, use_container_width=True, hide_index=True)
        
        with tab3:
            st.dataframe(df_filtered, use_container_width=True, hide_index=True)
            
            csv = df_filtered.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📥 Download Data CSV",
                csv,
                f'data_kependudukan_{selected_year}_filtered.csv',
                'text/csv'
            )
    
    else:  # Mode Perbandingan Multi Tahun
        st.markdown("### 📊 Perbandingan Antar Tahun")
        st.markdown("---")
        
        st.sidebar.subheader("📅 Pilih Tahun untuk Dibandingkan")
        available_years = sorted(df['tahun'].unique())
        selected_years = st.sidebar.multiselect(
            "Tahun:",
            options=available_years,
            default=available_years
        )
        
        if not selected_years:
            st.warning("⚠️ Pilih minimal 1 tahun untuk analisis")
            st.stop()
        
        df_comparison = df[df['tahun'].isin(selected_years)].copy()
        
        st.header("📊 Ringkasan Per Tahun")
        
        cols = st.columns(len(selected_years))
        
        for idx, year in enumerate(sorted(selected_years)):
            df_year_comp = df_comparison[df_comparison['tahun'] == year]
            total = df_year_comp['jumlah'].sum()
            male = df_year_comp[df_year_comp['kelamin'] == 'L']['jumlah'].sum()
            female = df_year_comp[df_year_comp['kelamin'] == 'P']['jumlah'].sum()
            
            with cols[idx]:
                st.metric(f"📅 Tahun {year}", format_number(total))
                st.caption(f"♂️ {format_number(male)}")
                st.caption(f"♀️ {format_number(female)}")
        
        st.markdown("---")
        
        st.header("📈 Trend Populasi Antar Tahun")
        
        df_years_selected = df[df['tahun'].isin(selected_years)]
        fig_trend_comp = create_year_trend_chart(df_years_selected)
        st.plotly_chart(fig_trend_comp, use_container_width=True)
        
        st.markdown("---")
        
        st.header("📋 Tabel Perbandingan Detail")
        
        summary_years = df_comparison.groupby('tahun').agg({
            'jumlah': 'sum',
            'kecamatan': 'nunique',
            'kelurahan': 'nunique'
        }).reset_index()
        
        male_counts = df_comparison[df_comparison['kelamin'] == 'L'].groupby('tahun')['jumlah'].sum()
        female_counts = df_comparison[df_comparison['kelamin'] == 'P'].groupby('tahun')['jumlah'].sum()
        
        summary_years['laki_laki'] = summary_years['tahun'].map(male_counts)
        summary_years['perempuan'] = summary_years['tahun'].map(female_counts)
        
        summary_years.columns = ['Tahun', 'Total Penduduk', 'Jumlah Kecamatan', 
                                'Jumlah Kelurahan', 'Laki-laki', 'Perempuan']
        
        summary_years = summary_years.sort_values('Tahun')
        summary_years['Pertumbuhan (%)'] = summary_years['Total Penduduk'].pct_change() * 100
        
        st.dataframe(summary_years, use_container_width=True, hide_index=True)
        
        csv_comp = df_comparison.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Download Data Perbandingan",
            csv_comp,
            'data_comparison_multi_year.csv',
            'text/csv'
        )
    
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: gray;'>
        <p>Dashboard Kependudukan Kota Samarinda | Data Tahun 2022-2024</p>
        <p>Sumber: Dinas Kependudukan dan Pencatatan Sipil Kota Samarinda</p>
        <p style='font-size: 0.85rem;'><em>Catatan: Penduduk berusia 75+ tahun digabung dalam satu kategori</em></p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()