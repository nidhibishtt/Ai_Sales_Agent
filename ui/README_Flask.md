# Flask AI Sales Agent UI

A modern, professional web interface for the AI Sales Agent built with Flask and WebSocket support.

## Features

### 🚀 **Modern Chat Interface**
- Real-time messaging with WebSocket support
- ChatGPT/Gemini-style chat bubbles with avatars
- Markdown rendering (code blocks, links, formatting)
- Typing indicators and smooth animations
- Auto-resizing input with multi-line support

### 🎨 **Professional Design**
- Dark/light theme toggle with system preference detection
- Responsive design for desktop and mobile
- Smooth animations and transitions
- Modern CSS with CSS custom properties
- Professional color scheme and typography

### ⚙️ **Advanced Controls**
- Model settings (temperature, max tokens, streaming)
- Conversation management with history
- Quick prompt buttons for common scenarios
- Export functionality (JSON format)
- System status monitoring

### 📊 **Analytics & Insights**
- Real-time entity extraction visualization
- Performance metrics and charts
- Conversation analytics
- Entity coverage tracking

### 🔧 **Technical Features**
- Flask backend with RESTful API
- WebSocket support via Flask-SocketIO
- Session management
- Real-time system status
- Auto-scroll chat history

## Quick Start

### 1. Install Dependencies
```bash
pip install flask flask-socketio
```

### 2. Launch the Application
```bash
# From project root
python ui/launch_flask.py
```

### 3. Access the UI
- **Local**: http://localhost:5000
- **Network**: http://192.168.1.6:5000

## File Structure

```
ui/
├── flask_app.py          # Main Flask application
├── launch_flask.py       # Launch script
├── templates/
│   └── chat.html         # Main HTML template
├── static/
│   ├── css/
│   │   └── style.css     # Modern CSS styles
│   └── js/
│       └── app.js        # Frontend JavaScript
├── streamlit_app.py      # Alternative Streamlit version
└── README.md            # This file
```

## API Endpoints

### `/` (GET)
Main chat interface

### `/api/system-status` (GET)
Returns system status and health information

### `/api/chat` (POST)
Process chat messages
```json
{
  "message": "Your hiring requirements here"
}
```

### WebSocket Events
- `connect` - Client connection established
- `disconnect` - Client disconnection
- `typing` - Typing indicator events

## Customization

### Theme Customization
Modify CSS custom properties in `static/css/style.css`:
```css
:root {
  --primary: #6366f1;
  --bg-body: #f5f7fb;
  /* ... other variables */
}
```

### Adding New Features
1. Add API endpoints in `flask_app.py`
2. Update frontend JavaScript in `static/js/app.js`
3. Modify HTML template in `templates/chat.html`
4. Update CSS styles in `static/css/style.css`

## Advantages over Streamlit

### ⚡ **Performance**
- Faster page loads and interactions
- Real-time WebSocket communication
- Better mobile performance
- More responsive UI updates

### 🎨 **Customization**
- Full control over HTML/CSS/JS
- Custom animations and interactions
- Professional styling capabilities
- Better responsive design

### 🔧 **Technical**
- RESTful API architecture
- WebSocket support for real-time features
- Session management
- Better scalability options

### 📱 **User Experience**
- Native browser features
- Better mobile experience
- Faster navigation
- More intuitive interactions

## Deployment Options

### Development
```bash
python ui/launch_flask.py
```

### Production
Use a production WSGI server like Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 ui.flask_app:app
```

### Docker
Create a Dockerfile for containerized deployment:
```dockerfile
FROM python:3.11-slim
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
EXPOSE 5000
CMD ["python", "ui/launch_flask.py"]
```

## Browser Support

- ✅ Chrome 80+
- ✅ Firefox 75+
- ✅ Safari 13+
- ✅ Edge 80+
- ✅ Mobile browsers

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.
