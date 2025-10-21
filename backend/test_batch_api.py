"""
Snel test script voor batch endpoints
"""
import requests
import os

BASE_URL = "http://localhost:8000/api"

def test_batch_creation():
    """Test het aanmaken van een batch"""
    print("\n1️⃣  Test: Batch aanmaken")
    response = requests.post(
        f"{BASE_URL}/batches/create",
        json={"name": "Test Batch - Week 42"}
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Batch aangemaakt: ID={data['id']}, Naam={data['name']}")
        return data['id']
    else:
        print(f"❌ Fout: {response.text}")
        return None


def test_pdf_upload(batch_id):
    """Test PDF upload naar batch"""
    print(f"\n2️⃣  Test: PDF uploaden naar batch {batch_id}")
    
    # Gebruik de dummy PDF
    pdf_path = "../dummyinfo/Interfiliaalverdeling vooraf - 423264.pdf"
    
    if not os.path.exists(pdf_path):
        print(f"❌ PDF niet gevonden: {pdf_path}")
        return
    
    with open(pdf_path, 'rb') as f:
        files = {'file': ('test.pdf', f, 'application/pdf')}
        response = requests.post(
            f"{BASE_URL}/batches/{batch_id}/upload",
            files=files
        )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Upload succesvol!")
        print(f"   Filename: {data['filename']}")
        print(f"   Status: {data['status']}")
        print(f"   Message: {data['message']}")
    else:
        print(f"❌ Fout: {response.text}")


def test_batch_details(batch_id):
    """Test batch details ophalen"""
    print(f"\n3️⃣  Test: Batch details ophalen (ID={batch_id})")
    
    response = requests.get(f"{BASE_URL}/batches/{batch_id}")
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Batch details:")
        print(f"   Naam: {data['name']}")
        print(f"   Status: {data['status']}")
        print(f"   PDF's: {data['pdf_count']}")
        print(f"   Verwerkt: {data['processed_count']}")
        if data['pdfs']:
            print(f"\n   PDF Details:")
            for pdf in data['pdfs']:
                print(f"     - {pdf['filename']}: {pdf['status']} ({pdf['extracted_count']} artikelen)")
    else:
        print(f"❌ Fout: {response.text}")


def main():
    print("=" * 60)
    print("🧪 BATCH API TEST")
    print("=" * 60)
    print("\n⚠️  Zorg dat de API server draait op http://localhost:8000")
    input("Druk op Enter om te starten...")
    
    # Test 1: Batch aanmaken
    batch_id = test_batch_creation()
    
    if batch_id:
        # Test 2: PDF uploaden
        test_pdf_upload(batch_id)
        
        # Test 3: Details ophalen
        test_batch_details(batch_id)
    
    print("\n" + "=" * 60)
    print("✅ Tests voltooid!")
    print("=" * 60)


if __name__ == "__main__":
    main()
