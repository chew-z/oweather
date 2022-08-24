package main

// Forecast - is as could be seen outside
type Forecast struct {
	Lat            float64 `json:"lat"`
	Lon            float64 `json:"lon"`
	Timezone       string  `json:"timezone"`
	TimezoneOffset int     `json:"timezone_offset"`
	Current        Current `json:"current"`
	Daily          Daily   `json:"daily"`
}

// Current -
type Current struct {
	Dt         int     `json:"dt"`
	Sunrise    int     `json:"sunrise"`
	Sunset     int     `json:"sunset"`
	Temp       float64 `json:"temp"`
	FeelsLike  float64 `json:"feels_like"`
	Pressure   int     `json:"pressure"`
	Humidity   int     `json:"humidity"`
	DewPoint   float64 `json:"dew_point"`
	Uvi        float64 `json:"uvi"`
	Clouds     int     `json:"clouds"`
	Visibility int     `json:"visibility"`
	WindSpeed  float64 `json:"wind_speed"`
	WindDeg    int     `json:"wind_deg"`
	Weather    Weather `json:"weather"`
}

// Daily --
type Daily []struct {
	Dt        int       `json:"dt"`
	Sunrise   int       `json:"sunrise"`
	Sunset    int       `json:"sunset"`
	Temp      Temp      `json:"temp"`
	FeelsLike FeelsLike `json:"feels_like"`
	Pressure  int       `json:"pressure"`
	Humidity  int       `json:"humidity"`
	DewPoint  float64   `json:"dew_point"`
	WindSpeed float64   `json:"wind_speed"`
	WindDeg   int       `json:"wind_deg"`
	Weather   Weather   `json:"weather"`
	Clouds    int       `json:"clouds"`
	Rain      float64   `json:"rain"`
	Uvi       float64   `json:"uvi"`
}

// Weather --
type Weather []struct {
	ID   int    `json:"id"`
	Main string `json:"main"`
	Desc string `json:"description"`
	Icon string `json:"icon"`
}

// Temp -
type Temp struct {
	Day   float64 `json:"day"`
	Min   float64 `json:"min"`
	Max   float64 `json:"max"`
	Night float64 `json:"night"`
	Eve   float64 `json:"eve"`
	Morn  float64 `json:"morn"`
}

// FeelsLike --
type FeelsLike struct {
	Day   float64 `json:"day"`
	Night float64 `json:"night"`
	Eve   float64 `json:"eve"`
	Morn  float64 `json:"morn"`
}
