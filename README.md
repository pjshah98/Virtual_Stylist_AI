
# Virtual Stylist AI
Modern AI-powered outfit recommendation platform built with Flask.

## 🌟 Features
- **Modern landing + stylist UI** with glassmorphism and animated gradient background
- **Outfit cards** in a responsive grid (3 per row on desktop)
- **ML-ranked recommendations** using the trained scikit-learn model (`predict_proba`)
- **Color harmony engine** (complementary / analogous / monochromatic)
- **Shuffle + regenerate** (re-runs the recommendation engine)
- **Favorites system** using browser `localStorage` + “My Saved Outfits” page
- **Dark mode toggle** using CSS variables

## 📱 Screens
### Landing
- Hero: **AI Powered Outfit Generator** / **Find the perfect outfit in seconds.**
- Buttons: **Generate Outfit**, **Explore Styles**

### Stylist
- Preferences: top/bottom/shoes + interactive color palette
- Inputs: **style preference** + **season**
- Results: ranked outfit cards + save/regenerate

## 🛠️ Technologies Used
- **Frontend**: HTML, CSS, JavaScript
- **Backend**: Python, Flask
- **Machine Learning**: scikit-learn, pandas
- **Other Libraries**: pickle for model serialization

## 📝 Setup Instructions
Follow these steps to set up the project locally:

### 1. Clone the Repository
```bash
git clone https://github.com/pjshah98/Virtual_Stylist_AI.git
cd Virtual_Stylist_AI
```

### 2. Create a Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows use: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
python3 -m pip install -r requirements.txt --user
```

### 4. Run the Application
```bash
python3 run.py
```

Open:
- `http://127.0.0.1:5000/` (Landing)
- `http://127.0.0.1:5000/stylist` (AI Stylist)
- `http://127.0.0.1:5000/saved` (My Saved Outfits)

## 📄 Project Structure
```plaintext
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── routes/
│   │   ├── main_routes.py
│   │   └── api_routes.py
│   ├── services/
│   │   ├── recommendation_service.py
│   │   ├── outfit_generator.py
│   │   └── color_service.py
│   ├── models/
│   │   └── model_loader.py
│   ├── templates/
│   │   ├── layout/
│   │   ├── pages/
│   │   └── components/
│   └── static/
│       ├── css/
│       ├── js/
│       └── images/
├── ml/
│   ├── fashion_trends.ipynb
│   ├── recommendation_engine.py
│   ├── dataset/
│   │   └── fashion_data_large.csv
│   └── models/
│       └── recommendation_model.pkl
├── tests/
│   └── test_routes.py
├── .gitignore
├── README.md
├── requirements.txt
└── run.py
```

## 🔌 API
- **POST** `/api/recommend` — returns `{ request, outfits }` where `outfits` are sorted by score
- **GET** `/api/presets` — returns available style presets

## 🔐 Security
- Set `SECRET_KEY` via environment variable:

```bash
export SECRET_KEY="your-secret"
```

## 📄 License
This project is licensed under the MIT License – see the LICENSE file for details.