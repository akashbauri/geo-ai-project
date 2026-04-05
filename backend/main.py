from fastapi import FastAPI
from pydantic import BaseModel
import requests
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv
from groq import Groq
import urllib3

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

load_dotenv()

app = FastAPI()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

class URLRequest(BaseModel):
    url: str

def scrape_website(url):
    try:
        # FIXED SSL ISSUE HERE
        response = requests.get(url, verify=False, timeout=10)

        soup = BeautifulSoup(response.text, "html.parser")

        title = soup.title.string if soup.title else "No title"

        meta_desc = ""
        desc_tag = soup.find("meta", attrs={"name": "description"})
        if desc_tag:
            meta_desc = desc_tag.get("content", "")

        headings = [h.text.strip() for h in soup.find_all(["h1", "h2", "h3"])]

        img = soup.find("img")
        img_url = img["src"] if img and "src" in img.attrs else ""

        return {
            "title": title,
            "description": meta_desc,
            "headings": headings[:5],
            "image": img_url
        }

    except Exception as e:
        return {"error": str(e)}

def generate_json_ld(data):
    try:
        prompt = f"""
        Generate JSON-LD schema for SEO.
        Title: {data['title']}
        Description: {data['description']}
        Headings: {data['headings']}

        Return ONLY valid JSON.
        """

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}]
        )

        return response.choices[0].message.content

    except Exception as e:
        return f"LLM Error: {str(e)}"

@app.get("/")
def home():
    return {"message": "GEO AI API Running 🚀"}

@app.post("/geo-audit")
def geo_audit(request: URLRequest):
    data = scrape_website(request.url)

    if "error" in data:
        return data

    json_ld = generate_json_ld(data)

    return {
        "page_data": data,
        "json_ld": json_ld
    }
