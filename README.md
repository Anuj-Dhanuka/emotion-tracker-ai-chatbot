# Daily Mood Journal AI Companion

A web application that helps you track your daily moods and provides empathetic AI responses using Google's Gemini API.

## Features

- Daily mood journaling with emotion detection
- AI-powered empathetic responses
- Mood tracking and visualization
- Clean, modern UI with responsive design
- Voice input option (coming soon)

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up environment variables:
   - Obtain a Gemini API key from Google Cloud Console
   - Set the `GEMINI_API_KEY` environment variable in your system or use a `.env` file
   - Make sure to never commit your `.env` file to version control

   Example for Windows:
   ```bash
   set GEMINI_API_KEY=your_api_key_here
   ```
   
   Or create a `.env` file locally (do not commit it):
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

3. Run the application:
```bash
python app.py
```

4. Open your browser and navigate to `http://localhost:5000`



## Technologies Used

- Backend: Python Flask
- Frontend: HTML, CSS, JavaScript
- Database: SQLite
- AI: Google Gemini API
- Visualization: Plotly.js

## Contributing

Feel free to submit issues and enhancement requests!

## License

This project is licensed under the MIT License - see the LICENSE file for details.
