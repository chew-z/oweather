package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"time"

	"github.com/IvanMenshykov/MoonPhase"
	_ "github.com/joho/godotenv/autoload"
	"github.com/kyokomi/emoji"
)

func main() {
	if len(os.Args) < 2 {
		w := weather("current")

		bft := wind2bft(w.Current.WindSpeed)
		mph := getPhaseString(time.Unix(int64(w.Current.Dt), 0))
		fmt.Printf("City: [%2.2f / %2.2f]\n", w.Lat, w.Lon)
		fmt.Printf("[ Sunrise: %s / Sunset: %s ]\n", time.Unix(int64(w.Current.Sunrise), 0).Format("15:04"), time.Unix(int64(w.Current.Sunset), 0).Format("15:04"))
		fmt.Printf("Moon phase: %s ", mph)
		emoji.Println(moonEmoji(mph))
		fmt.Printf("Weather: %s ", w.Current.Weather[0].Desc)
		emoji.Println(wEmoji(w.Current.Weather[0].Icon))
		// fmt.Printf("w: %s Icon: %s ", w.Current.Weather[0].Desc, w.Current.Weather[0].Icon)
		fmt.Printf("\tTemperature: %2.1f\u2103 feels like %2.1f\u2103\n", w.Current.Temp, w.Current.FeelsLike)
		// fmt.Printf("\tHigh: %2.1f\u2103 Low: %2.1f\u2103\n", w.Main.TempMax, w.Main.TempMin)
		fmt.Printf("\tHumidity: %d%%, Pressure: %dhPa\n", w.Current.Humidity, w.Current.Pressure)
		fmt.Printf("\tWind: %2.1fm/s from %d\u00b0\n", w.Current.WindSpeed, w.Current.WindDeg)
		fmt.Printf("\tWind: %2.1f knots %s / %s\n", wind2knots(w.Current.WindSpeed), deg2cardinal(w.Current.WindDeg), beaufort(bft, "label"))
		fmt.Printf("\tWind [land]: %dB - %s\n", bft, beaufort(bft, "land"))
		fmt.Printf("\tWind [sea]: %dB - %s\n", bft, beaufort(bft, "sea"))
		fmt.Printf("\tClouds: %d%%\n", w.Current.Clouds)
		fmt.Printf("\tDew point: %2.1f\u2103\n", w.Current.DewPoint)
		fmt.Printf("Time: %s\n", time.Unix(int64(w.Current.Dt), 0).Format("15:04"))
	} else {
		w := weather("daily")
		forecast := w.Daily
		for _, f := range forecast {
			mph := getPhaseString(time.Unix(int64(f.Dt), 0))
			bft := wind2bft(f.WindSpeed)
			fmt.Printf("%s ", time.Unix(int64(f.Dt), 0).Format("Mon Jan 2"))
			emoji.Println(moonEmoji(mph))
			fmt.Printf("%s ", f.Weather[0].Desc)
			emoji.Println(wEmoji(f.Weather[0].Icon))
			fmt.Printf("\tMorning : %2.1f\u2103 feels like %2.1f\u2103\n", f.Temp.Morn, f.FeelsLike.Morn)
			fmt.Printf("\tDay : %2.1f\u2103 feels like %2.1f\u2103\n", f.Temp.Day, f.FeelsLike.Day)
			fmt.Printf("\tEvening : %2.1f\u2103 feels like %2.1f\u2103\n", f.Temp.Eve, f.FeelsLike.Eve)
			fmt.Printf("\tNight : %2.1f\u2103 feels like %2.1f\u2103\n", f.Temp.Night, f.FeelsLike.Night)
			// fmt.Printf("\tHigh: %2.1f\u2103 Low: %2.1f\u2103\n", f.Temp.Max, f.Temp.Min)
			fmt.Printf("\tClouds: %d%%\n", f.Clouds)
			fmt.Printf("\tRain: %2.1fmm\n", f.Rain)
			fmt.Printf("\tHumidity: %d%%, Pressure: %dhPa\n", f.Humidity, f.Pressure)
			fmt.Printf("\tDew point: %2.1f\u2103\n", f.DewPoint)
			fmt.Printf("\tWind: %2.1f knots %s / %s\n", wind2knots(f.WindSpeed), deg2cardinal(f.WindDeg), beaufort(bft, "label"))
		}
	}
}

func weather(t string) *Forecast {

	var apiKey = os.Getenv("OWM_API_KEY")
	var params string
	baseurl := "https://api.openweathermap.org/data/2.5/onecall?%s"
	if t == "current" {
		params = fmt.Sprintf("lat=%s&lon=%s&units=%s&exclude=hourly,daily&appid=%s", "52.43", "20.89", "metric", apiKey)
	} else {
		params = fmt.Sprintf("lat=%s&lon=%s&units=%s&exclude=hourly,current&appid=%s", "52.43", "20.89", "metric", apiKey)
	}
	url := fmt.Sprintf(baseurl, params)
	client := http.Client{
		Timeout: time.Second * 3, // Timeout after 2 seconds
	}
	req, err := http.NewRequest(http.MethodGet, url, nil)
	if err != nil {
		log.Fatal(err)
	}
	req.Header.Set("User-Agent", "w-bot")

	res, getErr := client.Do(req)
	if getErr != nil {
		log.Fatal(getErr)
	}

	if res.Body != nil {
		defer res.Body.Close()
	}

	w := Forecast{}
	json.NewDecoder(res.Body).Decode(&w)

	return &w
}

func wEmoji(icon string) string {
	switch icon {
	case "01d":
		return ":sun:"
	case "02d":
		return ":sun_behind_small_cloud:"
	case "03d":
		return ":cloud:"
	case "04d":
		return ":sun_behind_large_cloud:"
	case "09d":
		return ":sun_behind_rain_cloud:"
	case "10d":
		return ":umbrella:"
	case "11d":
		return ":cloud_with_lighting:"
	case "13d":
		return ":snowflake:"
	case "50d":
		return ":fog:"
	default:
		return ":umbrella_with_rain_drops:"
	}
}

func moonEmoji(icon string) string {
	switch icon {
	case "New Moon":
		return ":new_moon:"
	case "Waxing Crescent":
		return ":waxing_crescent_moon:"
	case "First Quarter":
		return ":first_quarter_moon:"
	case "Waxing Gibbous":
		return ":waxing_gibbous_moon:"
	case "Full Moon":
		return ":full_moon:"
	case "Waning Gibbous":
		return ":waning_gibbous_moon:"
	case "Third Quarter":
		return ":last_quarter_moon:"
	case "Waning Crescent":
		return ":waning_crescent_moon:"
	default:
		return ":star:"
	}
}

func deg2cardinal(deg int) string {

	dirs := [16]string{"N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE", "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"}
	ix := int((float64(deg)+11.25)/22.5 - 0.02)
	return dirs[ix%16]
}

func wind2knots(ms float64) float64 {

	return ms * 3.6 / 1.852
}

func wind2bft(ms float64) int {

	bftThreshold := [12]float64{0.3, 1.5, 3.4, 5.4, 7.9, 10.7, 13.8, 17.1, 20.7, 24.4, 28.4, 32.6}

	for i, v := range bftThreshold {
		if ms < v {
			return i
		}
	}
	return 0
}

func dewPoint(temp float64, hum int) float64 {
	/* Compute dew point, using formula from
	http://en.wikipedia.org/wiki/Dew_point.
	https://iridl.ldeo.columbia.edu/dochelp/QA/Basic/dewpoint.html
	http;//dx.doi.org/10.1175/BAMS-86-2-225
	*/
	return temp - ((100.0 - float64(hum)) / 5.0)
}

func getPhaseString(dt time.Time) string {
	m := MoonPhase.New(dt)
	return m.PhaseName()
}

func beaufort(bft int, label string) string {
	beaufortSea := [13]string{
		"Sea like a mirror",
		"Ripples with the appearance of scales are formed, but without foam crests",
		"Small wavelets, still short, but more pronounced. Crests have a glassy appearance and do not break",
		"Large wavelets. Crests begin to break. Foam of glassy appearance. Perhaps scattered white horses",
		"Small waves, becoming larger; fairly frequent white horses",
		"Moderate waves, taking a more pronounced long form; many white horses are formed. Chance of some spray",
		"Large waves begin to form; the white foam crests are more extensive everywhere. Probably some spray",
		"Sea heaps up and white foam from breaking waves begins to be blown in streaks along the direction of the wind",
		"Moderately high waves of greater length; edges of crests begin to break into spindrift. The foam is blown in well-marked streaks along the direction of the wind",
		"High waves. Dense streaks of foam along the direction of the wind. Crests of waves begin to topple, tumble and roll over. Spray may affect visibility",
		"Very high waves with long over-hanging crests. The resulting foam, in great patches, is blown in dense white streaks along the direction of the wind. On the whole the surface of the sea takes on a white appearance. The tumbling of the sea becomes heavy and shock-like. Visibility affected",
		"Exceptionally high waves (small and medium-size ships might disappear behind the waves). The sea is completely covered with long white patches of foam flying along the direction of the wind. Everywhere the edges of the wave crests are blown into froth. Visibility affected",
		"The air is filled with foam and spray. Sea completely white with driving spray; visibility very seriously affected"}
	beaufortLand := [13]string{
		"Calm. Smoke rises vertically",
		"Wind motion visible in smoke",
		"Wind felt on exposed skin. Leaves rustle",
		"Leaves and smaller twigs in constant motion",
		"Dust and loose paper raised. Small branches begin to move",
		"Branches of a moderate size move. Small trees begin to sway",
		"Large branches in motion. Whistling heard in overhead wires. Umbrella use becomes difficult. Empty plastic garbage cans tip over",
		"Whole trees in motion. Effort needed to walk against the wind. Swaying of skyscrapers may be felt, especially by people on upper floors",
		"Twigs broken from trees. Cars veer on road",
		"Larger branches break off trees, and some small trees blow over. Construction/temporary signs and barricades blow over. Damage to circus tents and canopies",
		"Trees are broken off or uprooted, saplings bent and deformed, poorly attached asphalt shingles and shingles in poor condition peel off roofs",
		"Widespread vegetation damage. More damage to most roofing surfaces, asphalt tiles that have curled up and/or fractured due to age may break away completely",
		"Considerable and widespread damage to vegetation, a few windows broken, structural damage to mobile homes and poorly constructed sheds and barns. Debris may be hurled about"}
	beaufortLabel := [13]string{
		"Calm",
		"Light Air",
		"Light Breeze",
		"Gentle Breeze",
		"Moderate Breeze",
		"Fresh Breeze",
		"Strong Breeze",
		"Near Gale",
		"Gale",
		"Severe Gale",
		"Storm",
		"Violent Storm",
		"Hurricane"}

	if label == "sea" {
		return beaufortSea[bft]
	} else if label == "land" {
		return beaufortLand[bft]
	} else {
		return beaufortLabel[bft]
	}
}
