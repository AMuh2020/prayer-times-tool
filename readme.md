# Prayer Times Calendar Generator 🕌

A tool that converts prayer time schedules from PDF/image files into iCalendar (`.ics`) format, making it easy to import into any calendar application.

## 📖 Background

My university provides monthly prayer times as PDF or JPEG images. These times are more accurate than most prayer apps and include specific times for Jama'ah (congregational prayer) at the local mosque. Initially, I manually added prayer events to my calendar throughout the day, but this became cumbersome and I'd often forget. This tool automates the entire process by:

1. **Parsing** the prayer time image/PDF using Google's Gemini AI
2. **Converting** the extracted data into structured JSON
3. **Generating** a standard `.ics` calendar file that works with Google Calendar, Apple Calendar, Outlook, and more

The project includes both Python (original) and Go implementations. The Go version was created as a learning exercise while studying Go, and features additional customization options via command-line flags.

## ✨ Features

- 🤖 **AI-powered extraction**: Uses Gemini 2.5 Flash to intelligently parse prayer times from images
- 📅 **Universal compatibility**: Generates standard ICS files that work with all major calendar apps
- ⏰ **Customizable reminders**: Set reminder notifications before each prayer time
- 🌍 **Timezone support**: Properly handles Europe/London timezone (easily customizable)
- 🐍 **Python version**: Simple and straightforward implementation
- 🦫 **Go version**: Command-line tool with flag-based configuration for enhanced flexibility

## 🚀 Quick Start

### Prerequisites

- **Python version**: Python 3.8+
- **Go version**: Go 1.21+ (for the Go implementation)
- **Gemini API Key**: Required for AI-powered image parsing

### Get Your Gemini API Key

1. Visit [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Create a new API key
3. Set it as an environment variable:

```bash
export GEMINI_API_KEY='your-api-key-here'
# using powershell
# $Env:GEMINI_API_KEY = "your-api-key-here"
```

## 📦 Installation

### Python Version

```bash
# Clone the repository
git clone <repository-url>
cd prayer-times-tool

# Create and activate virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Go Version

```bash
cd go-version

# Install dependencies
go mod tidy

# Build the binary
go build -o prayer-times ./src
```

## 🎯 Usage

### Python Version

The Python version is interactive and will prompt you for input:

```bash
python main.py
```

**Example workflow:**
```bash
$ python main.py
Enter reminder time before prayer in minutes (default 10): 15
ICS file 'prayer_times.ics' created successfully.
```

**Key code snippet** - AI extraction using Gemini:

```python
def extract_prayer_times(image_bytes):
    # Define the JSON schema for structured output
    prayer_schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "month": types.Schema(type=types.Type.STRING),
            "year": types.Schema(type=types.Type.INTEGER),
            "daily_times": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.OBJECT,
                    properties={
                        "day": types.Schema(type=types.Type.INTEGER),
                        "Fajr": types.Schema(type=types.Type.STRING),
                        "Sunrise": types.Schema(type=types.Type.STRING),
                        "Dhuhr": types.Schema(type=types.Type.STRING),
                        "Asr": types.Schema(type=types.Type.STRING),
                        "Maghrib": types.Schema(type=types.Type.STRING),
                        "Isha": types.Schema(type=types.Type.STRING),
                    },
                    required=["day", "Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"],
                ),
            ),
        }
    )

    image_part = types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
    prompt = "Extract all the prayer times from this schedule image."
    
    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=[prompt, image_part],
        config=types.GenerateContentConfig(
            response_mime_type="application/json", 
            response_schema=prayer_schema
        )
    )
    
    return response.text
```

**Key code snippet** - Creating calendar events:

```python
def create_event(day, prayer_name, prayer_time, reminders_before_minutes, tz):
    event = Event()
    event.add('summary', f'{prayer_name} Prayer')
    event.add('description', f'Time for {prayer_name} prayer.')
    event.add('location', vText("Grey's prayer room or Elvet prayer room"))
    event.add('uid', f'Prayer-{prayer_name.lower()}-{day}-{prayer_time.replace(":", "")}@amalworks.dev')

    # Convert 12-hour to 24-hour format based on prayer type
    hour, minute = map(int, prayer_time.split(':'))
    if prayer_name in ['Fajr', 'Sunrise']:
        pass  # Already AM
    elif prayer_name == 'Dhuhr':
        if hour < 10:
            hour += 12
    else:  # Asr, Maghrib, Isha
        if hour != 12:
            hour += 12

    start_time = datetime(2025, 11, day, hour, minute, 0)
    end_time = start_time + timedelta(minutes=15)
    event.add('dtstart', tz.localize(start_time))
    event.add('dtend', tz.localize(end_time))
    
    # Add reminder alarm
    alarm = Alarm()
    alarm.add("trigger", timedelta(minutes=-reminders_before_minutes))
    alarm.add("action", "DISPLAY")
    alarm.add("description", f"Reminder: {prayer_name} prayer in {reminders_before_minutes} minutes.")
    event.add_component(alarm)
    
    return event
```

### Go Version

The Go version offers command-line flags for more control:

```bash
./prayer-times -file <path-to-json> [-reminder <minutes>] [-duration <minutes>]
```

**Examples:**

```bash
# Basic usage with default 10-minute reminder
./prayer-times -file ../test_november.json

# Custom 15-minute reminder
./prayer-times -file ../test_november.json -reminder 15

# Using a different JSON file
./prayer-times -file prayer_data_december.json -reminder 5
```

**Key code snippet** - Go implementation highlights:

```go
func main() {
    // Parse command-line flags
    filename := flag.String("file", "", "Path to the prayer times JSON file (required)")
    reminderMinutes := flag.Int("reminder", 10, "Reminder time before prayer in minutes")
    duration := flag.Int("duration", 15, "Duration of each prayer event in minutes")
    flag.Parse()

    // Validate and read JSON
    data, err := os.ReadFile(*filename)
    if err != nil {
        log.Fatalf("Error reading file: %v", err)
    }

    var prayerData PrayerData
    json.Unmarshal(data, &prayerData)

    // Create calendar
    cal := ics.NewCalendar()
    cal.SetProductId(fmt.Sprintf("-//Durham Prayer Times for %s %d//com.amalworks.prayer_times//", 
        prayerData.Month, prayerData.Year))

    // Generate events for each prayer
    prayers := []string{"Fajr", "Sunrise", "Dhuhr", "Asr", "Maghrib", "Isha"}
    for _, dailyTime := range prayerData.DailyTimes {
        for _, prayerName := range prayers {
            event := createEvent(prayerData.Year, getMonthNumber(prayerData.Month), 
                dailyTime.Day, prayerName, getPrayerTime(dailyTime, prayerName), 
                *reminderMinutes, *duration, loc)
            cal.AddVEvent(event)
        }
    }

    // Write ICS file
    cal.SerializeTo(f)
}
```

## 📁 Project Structure

```
prayer-times-tool/
├── main.py                      # Python implementation (main script)
├── ai_reader.py                 # Gemini AI integration for image parsing
├── reader.py                    # Legacy/alternative reader
├── requirements.txt             # Python dependencies
├── test_november.json           # Sample extracted data
├── prayer_times_november.png    # Sample input image
├── prayer_times_december.png    # Another sample image
├── prayer_times.ics            # Generated output file
├── go-version/                 # Go implementation
│   ├── src/
│   │   └── main.go            # Go source code
│   ├── go.mod                 # Go module definition
│   ├── go.sum                 # Go dependency checksums
│   ├── prayer-times           # Compiled binary
│   └── README.md              # Go-specific documentation
└── readme.md                   # This file
```

## 🔧 How It Works

### 1. Image Extraction (AI-Powered)

The tool uses Google's Gemini 2.0 Flash model with structured output to extract prayer times:

- **Input**: JPEG/PNG image of prayer schedule
- **Process**: Gemini analyzes the image and extracts data according to a predefined JSON schema
- **Output**: Structured JSON with month, year, and daily prayer times

### 2. Time Conversion

Prayer times are typically in 12-hour format. The tool intelligently converts them to 24-hour format:

- **Fajr & Sunrise**: Always AM (no conversion needed)
- **Dhuhr**: If hour < 10, add 12 (handles 12 PM correctly)
- **Asr, Maghrib, Isha**: Always PM (add 12 if not already 12)

### 3. ICS Generation

The tool creates a standard iCalendar file with:

- ✅ Individual events for each prayer time
- ✅ 15-minute duration per event
- ✅ Customizable reminder alarms
- ✅ Proper timezone handling (Europe/London)
- ✅ Unique UIDs for each event
- ✅ Location information

## 📋 JSON Format

The intermediate JSON format extracted by Gemini:

```json
{
    "month": "November",
    "year": 2025,
    "daily_times": [
        {
            "day": 1,
            "Fajr": "5:28",
            "Sunrise": "7:10",
            "Dhuhr": "11:50",
            "Asr": "2:01",
            "Maghrib": "4:29",
            "Isha": "6:11"
        },
        {
            "day": 2,
            "Fajr": "5:29",
            "Sunrise": "7:12",
            "Dhuhr": "11:50",
            "Asr": "1:59",
            "Maghrib": "4:27",
            "Isha": "6:09"
        }
        // ... more days
    ]
}
```

## 🎓 Learning Notes

This project served as a practical learning exercise:

- **Python → Go translation**: Understanding language paradigms and idioms
- **AI integration**: Using Google's Gemini for structured data extraction
- **Calendar standards**: Working with the iCalendar (RFC 5545) format
- **CLI design**: Building user-friendly command-line interfaces in Go

## 🌐 Deployment

The Go version will be available on my website soon for easy browser-based usage. Stay tuned!

## 🔑 Environment Variables

The tool requires the following environment variable:

```bash
export GEMINI_API_KEY='your-api-key-here'
```

## 🛠️ Dependencies

### Python

- `google-genai` - Google Gemini AI SDK
- `icalendar` - ICS file generation
- `pytz` - Timezone handling

### Go

- `github.com/arran4/golang-ical` - ICS file generation in Go

## 📝 Example Output

After running the tool, you'll get a `prayer_times.ics` file that you can:

1. **Import to Google Calendar**: Settings → Import & Export → Import
2. **Add to Apple Calendar**: File → Import
3. **Use with Outlook**: File → Open & Export → Import/Export
4. **Any other calendar app**: Look for import/add calendar options

Each prayer time will appear as a separate event with your chosen reminder time and duration.

## 🤝 Contributing

Feel free to fork, improve, and submit pull requests. Some ideas for enhancement:

- Support for multiple timezones
- Web interface for drag-and-drop image upload
- Batch processing for multiple months
- Different reminder configurations per prayer
- Support for additional calendar formats

## 📄 License

This project is open source and available for personal and educational use.

## 🙏 Acknowledgments

- Durham University Islamic Society for providing accurate prayer times
- Google's Gemini AI for powerful image understanding capabilities
- The open-source community for excellent libraries

---

**Built with ❤️ to make daily prayer time management effortless**
