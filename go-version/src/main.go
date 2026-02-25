package main

import (
	"encoding/json"
	"flag"
	"fmt"
	"log"
	"os"
	"time"

	ics "github.com/arran4/golang-ical"
)

type Data struct {
	Months []PrayerData `json:"months"`
}

type PrayerData struct {
	Month      string      `json:"month"`
	Year       int         `json:"year"`
	DailyTimes []DailyTime `json:"daily_times"`
}

type DailyTime struct {
	Day  int    `json:"day"`
	Fajr string `json:"Fajr"`
	// Sunrise string `json:"Sunrise"`
	Dhuhr   string `json:"Dhuhr"`
	Asr     string `json:"Asr"`
	Maghrib string `json:"Maghrib"`
	Isha    string `json:"Isha"`
}

func main() {
	// Define command-line flags
	filename := flag.String("file", "", "Path to the prayer times JSON file (required)")
	reminderMinutes := flag.Int("reminder", 10, "Reminder time before prayer in minutes")
	duration := flag.Int("duration", 15, "Duration of each prayer event in minutes")
	flag.Parse()

	// Validate required flag
	if *filename == "" {
		fmt.Println("Error: -file flag is required")
		flag.Usage()
		os.Exit(1)
	}

	// Read and parse the JSON file
	data, err := os.ReadFile(*filename)
	if err != nil {
		log.Fatalf("Error reading file: %v", err)
	}

	var dataStruct Data
	if err := json.Unmarshal(data, &dataStruct); err != nil {
		log.Fatalf("Error parsing JSON: %v", err)
	}

	// Create calendar
	cal := ics.NewCalendar()
	cal.SetVersion("2.0")

	// get the first month data
	firstMonthName := dataStruct.Months[0].Month
	firstMonthYear := dataStruct.Months[0].Year
	lastMonthName := dataStruct.Months[len(dataStruct.Months)-1].Month
	lastMonthYear := dataStruct.Months[len(dataStruct.Months)-1].Year
	firstDay := dataStruct.Months[0].DailyTimes[0].Day
	lastDay := dataStruct.Months[len(dataStruct.Months)-1].DailyTimes[len(dataStruct.Months[len(dataStruct.Months)-1].DailyTimes)-1].Day

	prodID := "Durham Prayer Times for"
	calname := ""

	if firstMonthName == lastMonthName && firstMonthYear == lastMonthYear {
		prodID += fmt.Sprintf(" %s %d", firstMonthName, firstMonthYear)
		calname = fmt.Sprintf("Prayer Times Month: %s %d", firstMonthName, firstMonthYear)
	} else {
		prodID += fmt.Sprintf(" %d %s %d to %d %s %d", firstDay, firstMonthName, firstMonthYear, lastDay, lastMonthName, lastMonthYear)
		calname = fmt.Sprintf("Prayer Times: %d %s %d to %d %s %d", firstDay, firstMonthName, firstMonthYear, lastDay, lastMonthName, lastMonthYear)
	}

	cal.SetCalscale("GREGORIAN")
	cal.SetName(calname)
	cal.SetProductId(prodID)
	// Set timezone
	loc, err := time.LoadLocation("Europe/London")
	if err != nil {
		log.Fatalf("Error loading timezone: %v", err)
	}

	for _, prayerData := range dataStruct.Months {
		// Create events for each prayer time
		prayers := []string{"Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"} // Excluding Sunrise
		for _, dailyTime := range prayerData.DailyTimes {
			for _, prayerName := range prayers {
				prayerTime := getPrayerTime(dailyTime, prayerName)
				event := createEvent(prayerData.Year, getMonthNumber(prayerData.Month), dailyTime.Day, prayerName, prayerTime, *reminderMinutes, *duration, loc)
				cal.AddVEvent(event)
			}
		}
	}

	// Write to file
	outputFile := fmt.Sprintf("prayer_times_%s_%d.ics", firstMonthName, firstMonthYear)
	f, err := os.Create(outputFile)
	if err != nil {
		log.Fatalf("Error creating output file: %v", err)
	}
	defer f.Close()

	if err := cal.SerializeTo(f); err != nil {
		log.Fatalf("Error writing calendar: %v", err)
	}

	fmt.Printf("ICS file '%s' created successfully.\n", outputFile)
}

func getPrayerTime(dailyTime DailyTime, prayerName string) string {
	switch prayerName {
	case "Fajr":
		return dailyTime.Fajr
	// case "Sunrise":
	// 	return dailyTime.Sunrise
	case "Dhuhr":
		return dailyTime.Dhuhr
	case "Asr":
		return dailyTime.Asr
	case "Maghrib":
		return dailyTime.Maghrib
	case "Isha":
		return dailyTime.Isha
	default:
		return ""
	}
}

func createEvent(year, month, day int, prayerName, prayerTime string, reminderMinutes int, duration int, loc *time.Location) *ics.VEvent {
	event := ics.NewEvent(fmt.Sprintf("Prayer-%s-%d-%s@amalworks.dev", prayerName, day, prayerTime))
	event.SetSummary(fmt.Sprintf("%s Prayer", prayerName))
	event.SetDescription(fmt.Sprintf("Time for %s prayer.", prayerName))
	event.SetLocation("Grey/Elvet prayer room")

	// Convert 12-hour format to 24-hour format
	hour, minute := parseTime(prayerTime)
	hour = convertTo24Hour(prayerName, hour)

	// Create start and end times
	startTime := time.Date(year, time.Month(month), day, hour, minute, 0, 0, loc)
	endTime := startTime.Add(time.Duration(duration) * time.Minute) // duration minutes for prayer

	event.SetStartAt(startTime)
	event.SetEndAt(endTime)
	event.SetDtStampTime(time.Now())

	// Add alarm/reminder
	alarm := event.AddAlarm()
	alarm.SetAction(ics.ActionDisplay)
	alarm.SetTrigger(fmt.Sprintf("-PT%dM", reminderMinutes))
	alarm.SetDescription(fmt.Sprintf("Reminder: %s prayer in %d minutes.", prayerName, reminderMinutes))

	return event
}

func parseTime(timeStr string) (int, int) {
	var hour, minute int
	fmt.Sscanf(timeStr, "%d:%d", &hour, &minute)
	return hour, minute
}

func convertTo24Hour(prayerName string, hour int) int {
	// Fajr and Sunrise are always AM
	if prayerName == "Fajr" || prayerName == "Sunrise" {
		return hour
	}

	// Dhuhr: if hour < 10, add 12
	if prayerName == "Dhuhr" {
		if hour < 10 {
			return hour + 12
		}
		return hour
	}

	// Asr, Maghrib, Isha: if not 12, add 12
	if hour != 12 {
		return hour + 12
	}
	return hour
}

func getMonthNumber(monthName string) int {
	months := map[string]int{
		"January":   1,
		"February":  2,
		"March":     3,
		"April":     4,
		"May":       5,
		"June":      6,
		"July":      7,
		"August":    8,
		"September": 9,
		"October":   10,
		"November":  11,
		"December":  12,
	}
	return months[monthName]
}
