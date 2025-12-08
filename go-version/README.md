# Prayer Times Tool (Go Version)

A command-line tool to convert prayer times JSON data into an ICS (iCalendar) file.

## Building

```bash
cd go-version
go build -o prayer-times ./src
```

## Usage

```bash
./prayer-times -file <path-to-json-file> [-reminder <minutes>]
```

### Arguments

- `-file` (required): Path to the prayer times JSON file
- `-reminder` (optional): Reminder time before prayer in minutes (default: 10)

### Examples

```bash
# Using default reminder time (10 minutes)
./prayer-times -file ../test_november.json

# Custom reminder time
./prayer-times -file ../test_november.json -reminder 15
```

## Output

The tool generates a `prayer_times.ics` file in the current directory that can be imported into calendar applications.

## JSON Format

The input JSON file should have the following structure:

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
        }
    ]
}
```
