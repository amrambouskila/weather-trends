import json
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import requests


class GlobalWeatherAnalyzer:
    def __init__(self) -> None:
        self.base_url = "https://archive-api.open-meteo.com/v1/archive"

        # Define representative locations across the globe for better coverage
        self.locations = [
            {"name": "New York", "lat": 40.7128, "lon": -74.0060},
            {"name": "London", "lat": 51.5074, "lon": -0.1278},
            {"name": "Tokyo", "lat": 35.6762, "lon": 139.6503},
            {"name": "Sydney", "lat": -33.8688, "lon": 151.2093},
            {"name": "Cairo", "lat": 30.0444, "lon": 31.2357},
            {"name": "Rio de Janeiro", "lat": -22.9068, "lon": -43.1729},
            {"name": "Mumbai", "lat": 19.0760, "lon": 72.8777},
            {"name": "Moscow", "lat": 55.7558, "lon": 37.6173},
            {"name": "Beijing", "lat": 39.9042, "lon": 116.4074},
            {"name": "Cape Town", "lat": -33.9249, "lon": 18.4241},
            {"name": "Los Angeles", "lat": 34.0522, "lon": -118.2437},
            {"name": "Singapore", "lat": 1.3521, "lon": 103.8198}
        ]

        self.raw_data = None
        
    def fetch_weather_data(
        self,
        lat: float,
        lon: float,
        start_date: str,
        end_date: str,
    ) -> dict | str | None:
        """Fetch weather data from Open-Meteo API for a specific location"""
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date,
            "end_date": end_date,
            "daily": 'temperature_2m_mean',
            "timezone": "UTC"
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            
            # Print detailed error information
            print(f"URL: {response.url}")
            print(f"Status Code: {response.status_code}")
            
            if response.status_code != 200:
                text = response.text
                if (
                    "Hourly API request limit exceeded" in text
                    or "Daily API request limit exceeded" in text
                ):
                    return 'limit exceeded'

                print(f"Response content: {response.text}")
                time.sleep(60)
                return self.fetch_weather_data(lat, lon, start_date, end_date)
                
            data = response.json()
            
            # Debug: print the response to understand the API structure
            print(f"Debug - Response keys: {list(data.keys())}")
            if data and 'daily' in data:
                print(f"Debug - Daily data keys: {list(data['daily'].keys())}")
            
            return data
        except requests.exceptions.RequestException:
            return None
        except json.JSONDecodeError:
            return None

    def collect_global_data(self) -> pd.DataFrame | None:
        """Collect weather data from all representative locations"""
        start_date = '1940-01-01'
        end_date = '2025-12-31'
        print(f"Fetching weather data from {start_date} to {end_date}...")

        all_data = []
        
        # Fetch temperature data
        print("Fetching temperature data...")
        for i, location in enumerate(self.locations):
            print(f"Fetching temperature data for {location['name']} ({i+1}/{len(self.locations)})...")

            data = self.fetch_weather_data(
                location['lat'],
                location['lon'],
                start_date,
                end_date
            )

            if data == 'limit exceeded':
                return

            if data and 'daily' in data:
                df = pd.DataFrame(data['daily'])
                df['location'] = location['name']
                df['lat'] = location['lat']
                df['lon'] = location['lon']
                all_data.append(df)
        
        if not all_data:
            return
        
        # Combine all temperature data
        combined_data = pd.concat(all_data, ignore_index=True)
        if combined_data.shape[0] > 0:
            return combined_data

    def mock_weather_data(
            self,
            locations: list[dict],
            start_date: str = "1990-01-01",
            end_date: str = "2025-12-31",
            freq: str = "D",
            trend_c_per_year: float = 0.02,  # warming signal
            residual_loc_std: float = 0.8,  # small location-specific bias (after lat model)
            daily_noise_std: float = 1.2,  # day-to-day variability
            ar1_phi: float = 0.75,  # autocorrelation (weather persistence)
            missing_rate: float = 0.0,
            seed: int = 42,
    ) -> pd.DataFrame:
        """
        Returns a DataFrame compatible with visualize_weather_data():
          columns: time, temperature_2m_mean, location, lat, lon
        More realistic:
          - baseline mean temp depends on latitude
          - seasonality amplitude depends on latitude and hemisphere phase
          - AR(1) day-to-day noise (weather persistence)
          - linear warming trend
        """
        rng = np.random.default_rng(seed)
        dates = pd.date_range(start=start_date, end=end_date, freq=freq)
        n = len(dates)

        # fractional year for linear trend
        years = dates.year.to_numpy()
        frac_year = years + (dates.dayofyear.to_numpy() - 1) / 365.25
        year0 = float(pd.Timestamp(start_date).year)

        doy = dates.dayofyear.to_numpy()

        rows = []
        for loc in locations:
            lat = float(loc["lat"])
            lon = float(loc["lon"])

            # --- baseline mean temp by latitude (rough heuristic) ---
            # Near equator warmer; poles colder
            base_mean = 28.0 - 0.45 * abs(lat)  # e.g., 28C at equator, ~8C at 45°, ~0C at 62°

            # --- seasonality amplitude by latitude ---
            # Bigger seasonal swing at higher latitudes
            amp = 3.0 + 0.22 * abs(lat)  # ~3C at equator, ~13C at 45°, ~17C at 65°

            # --- hemisphere phase shift (southern hemisphere reversed seasons) ---
            phase_shift = 182 if lat < 0 else 0
            seasonal = amp * np.sin(2 * np.pi * ((doy + phase_shift) / 365.25))

            # --- AR(1) noise for realistic persistence ---
            eps = rng.normal(0.0, daily_noise_std, size=n)
            ar = np.empty(n, dtype=float)
            ar[0] = eps[0]
            for i in range(1, n):
                ar[i] = ar1_phi * ar[i - 1] + eps[i]

            # --- small location-specific residual (after lat model) ---
            loc_residual = rng.normal(0.0, residual_loc_std)

            # --- warming trend ---
            trend = trend_c_per_year * (frac_year - year0)

            temp = base_mean + seasonal + loc_residual + trend + ar

            df_loc = pd.DataFrame(
                {
                    "time": dates.strftime("%Y-%m-%d"),
                    "temperature_2m_mean": temp.astype(float),
                    "location": loc["name"],
                    "lat": lat,
                    "lon": lon,
                }
            )

            if 0.0 < missing_rate < 1.0:
                mask = rng.random(n) < missing_rate
                df_loc.loc[mask, "temperature_2m_mean"] = np.nan

            rows.append(df_loc)

        out = pd.concat(rows, ignore_index=True)

        # optionally drop some rows entirely
        if 0.0 < missing_rate < 1.0:
            drop_mask = rng.random(len(out)) < (missing_rate * 0.15)
            out = out.loc[~drop_mask].reset_index(drop=True)

        return out

    def visualize_weather_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate yearly averages for temperature and humidity"""
        # Convert date column to datetime
        df['time'] = pd.to_datetime(df['time'])
        
        # Extract year
        df['year'] = df['time'].dt.year

        # 1) Location-year averages (you already do this)
        loc_year = (
            df.groupby(["year", "location"])["temperature_2m_mean"]
            .mean()
            .reset_index()
        )

        # 2) Convert to anomalies per location (removes baseline climate differences)
        #    Use each location's long-run mean across all years as its baseline.
        loc_baseline = (
            loc_year.groupby("location")["temperature_2m_mean"]
            .mean()
            .rename("baseline")
            .reset_index()
        )

        loc_year = loc_year.merge(loc_baseline, on="location", how="left")
        loc_year["temp_anomaly"] = loc_year["temperature_2m_mean"] - loc_year["baseline"]

        # 3) Yearly mean anomaly + CI across locations
        yearly = (
            loc_year.groupby("year")["temp_anomaly"]
            .agg(mean="mean", std="std", n="count")
            .reset_index()
            .sort_values("year")
        )

        yearly["se"] = yearly["std"] / np.sqrt(yearly["n"])
        yearly["ci95"] = 1.96 * yearly["se"]

        # 4) Keep generate_summary_report() compatible:
        #    Put anomaly into the existing 'temperature_2m_mean' column name.
        yearly_avg = (
            yearly.set_index("year")
            .rename(columns={"mean": "temperature_2m_mean"})
        )

        # --- Trend regression: slope + p-value (SciPy if available; fallback otherwise) ---
        x = yearly_avg.index.to_numpy(dtype=float)
        y = yearly_avg["temperature_2m_mean"].to_numpy(dtype=float)

        slope = intercept = p_value = r2 = np.nan

        # Prefer SciPy for accurate p-value
        try:
            from scipy import stats  # type: ignore
            res = stats.linregress(x, y)
            slope = res.slope
            intercept = res.intercept
            p_value = res.pvalue
            r2 = res.rvalue ** 2
        except Exception:
            # Fallback: compute slope/intercept via polyfit; p-value via t-test formula
            # (uses normal equations + Student-t approximation)
            slope, intercept = np.polyfit(x, y, 1)

            n = len(x)
            if n >= 3:
                y_hat = slope * x + intercept
                resid = y - y_hat
                sse = np.sum(resid ** 2)
                sxx = np.sum((x - x.mean()) ** 2)

                if sxx > 0:
                    se_slope = np.sqrt((sse / (n - 2)) / sxx)
                    t_stat = slope / se_slope if se_slope > 0 else np.inf

                    # Try SciPy just for survival function if present; else normal approx
                    try:
                        from scipy.stats import t as tdist  # type: ignore
                        p_value = 2 * tdist.sf(np.abs(t_stat), df=n - 2)
                    except Exception:
                        # Normal approx for large df
                        from math import erf, sqrt
                        # two-sided p from normal CDF
                        z = np.abs(t_stat)
                        p_value = 2 * (1 - 0.5 * (1 + erf(z / sqrt(2))))

                    # r^2
                    sst = np.sum((y - y.mean()) ** 2)
                    r2 = 1 - (sse / sst) if sst > 0 else np.nan


        # --- Plot: trend + error bars + distribution ---
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))

        yerr = yearly_avg["ci95"].to_numpy(dtype=float)

        ax1.errorbar(
            x, y, yerr=yerr,
            fmt="o-", linewidth=2, markersize=3,
            capsize=3, elinewidth=1
        )
        ax1.set_title("Average Global Temperature Trend (with 95% CI)")
        ax1.set_xlabel("Year")
        ax1.set_ylabel("Temperature (°C)")
        ax1.grid(True, alpha=0.3)

        # Trend line + annotation
        trend_y = slope * x + intercept
        ax1.plot(x, trend_y, "--", alpha=0.8)

        # Put stats in legend (kept concise)
        if np.isfinite(p_value):
            ax1.legend([f"Trend: {slope:.4f}°C/year | p={p_value:.3g} | R²={r2:.3f}"])
        else:
            ax1.legend([f"Trend: {slope:.4f}°C/year"])

        # Distribution of yearly means
        ax2.hist(yearly_avg["temperature_2m_mean"], bins=20, alpha=0.7, edgecolor="black")
        ax2.set_title("Temperature Distribution (Yearly Means)")
        ax2.set_xlabel("Temperature (°C)")
        ax2.set_ylabel("Frequency")
        ax2.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

        return yearly_avg
        
    def generate_summary_report(self, yearly_avg: pd.DataFrame) -> None:
        """Generate a summary report of the findings"""
        print("=" * 60)
        print("GLOBAL WEATHER ANALYSIS SUMMARY REPORT")
        print("="*60)
        
        print(f"Data Range: {yearly_avg.index.min()} - {yearly_avg.index.max()}")
        print(f"Total Years Analyzed: {len(yearly_avg)}")
        
        temp_stats = yearly_avg['temperature_2m_mean'].describe()
        
        print("TEMPERATURE STATISTICS:")
        print(f"Mean: {temp_stats['mean']:.2f}°C")
        print(f"Min: {temp_stats['min']:.2f}°C ({yearly_avg.loc[yearly_avg['temperature_2m_mean'].idxmin()]})")
        print(f"Max: {temp_stats['max']:.2f}°C ({yearly_avg.loc[yearly_avg['temperature_2m_mean'].idxmax()]})")
        print(f"Std Dev: {temp_stats['std']:.2f}°C")
        
        # Calculate trends
        temp_trend = np.polyfit(yearly_avg.index, yearly_avg['temperature_2m_mean'], 1)[0]
        
        print("TRENDS:")
        print(f"Temperature Trend: {temp_trend:.4f}°C per year")
        
        # Calculate decade averages
        yearly_avg['decade'] = (yearly_avg.index // 10) * 10
        decade_avg = yearly_avg.groupby('decade').agg({
            'temperature_2m_mean': 'mean',
        }).reset_index()
        
        print("DECADE AVERAGES:")
        for _, row in decade_avg.iterrows():
            print(f"{int(row['decade'])}s: {row['temperature_2m_mean']:.2f}°C")
        
        print("=" * 60)

    def run_analysis(self) -> None:
        """Run the complete weather analysis"""
        try:
            # Collect data
            print("Step 1: Collecting global weather data...")
            self.raw_data = self.collect_global_data()

            if not isinstance(self.raw_data, pd.DataFrame):
                print('Reached API Limit -- resorting to mock weather data')
                self.raw_data = self.mock_weather_data(
                    locations=analyzer.locations,
                    trend_c_per_year=0.015,
                    daily_noise_std=1.0,
                    residual_loc_std=0.5,
                    seed=1
                )
            
            # Calculate yearly averages
            print("Step 2: Calculating yearly averages...")
            yearly_avg = self.visualize_weather_data(self.raw_data)
            
            # Generate summary report
            print("Step 4: Generating summary report...")
            self.generate_summary_report(yearly_avg)
            
            print("\nAnalysis complete! Check the generated charts")
            
        except Exception as e:
            print(f"Error during analysis: {e}")
            raise


if __name__ == "__main__":
    analyzer = GlobalWeatherAnalyzer()
    analyzer.run_analysis()
