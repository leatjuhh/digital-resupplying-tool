"""
Test script to verify the verkocht fix for article 424205
"""
import requests
import os

# API endpoints
BASE_URL = "http://localhost:8000"
PDF_PATH = os.path.join(os.path.dirname(__file__), "..", "dummyinfo", "424205.pdf")

def test_verkocht_totaal():
    """Test if verkocht totaal is correct after the fix"""
    
    print("=" * 60)
    print("Testing Verkocht Fix for Article 424205")
    print("=" * 60)
    print()
    
    # Step 1: Upload PDF
    print("Step 1: Uploading PDF...")
    
    with open(PDF_PATH, 'rb') as f:
        files = {'files': ('424205.pdf', f, 'application/pdf')}
        data = {'batch_name': 'Verkocht Fix Test'}
        
        response = requests.post(
            f"{BASE_URL}/api/pdf/ingest",
            files=files,
            data=data
        )
    
    if response.status_code != 200:
        print(f"❌ Failed to upload PDF: {response.status_code}")
        print(response.text)
        return False
    
    result = response.json()
    print(f"✅ PDF uploaded successfully")
    print(f"   Batch ID: {result['batch_id']}")
    print(f"   Proposals generated: {result['proposals_generated']}")
    print()
    
    batch_id = result['batch_id']
    
    # Step 2: Get batch proposals
    print("Step 2: Fetching proposals...")
    
    response = requests.get(f"{BASE_URL}/api/pdf/batches/{batch_id}/proposals")
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch proposals: {response.status_code}")
        return False
    
    proposals = response.json()
    
    if not proposals['proposals']:
        print("❌ No proposals found")
        return False
    
    # Find the proposal for article 424205
    proposal_id = proposals['proposals'][0]['id']
    print(f"✅ Found proposal ID: {proposal_id}")
    print()
    
    # Step 3: Get full proposal with inventory
    print("Step 3: Fetching full proposal data...")
    
    response = requests.get(f"{BASE_URL}/api/pdf/proposals/{proposal_id}/full")
    
    if response.status_code != 200:
        print(f"❌ Failed to fetch proposal details: {response.status_code}")
        return False
    
    proposal = response.json()
    print(f"✅ Retrieved proposal for article {proposal['artikelnummer']}")
    print()
    
    # Step 4: Calculate verkocht totaal
    print("Step 4: Calculating verkocht totaal...")
    print()
    
    total_verkocht = sum(store['sold'] for store in proposal['stores'])
    
    print("Store breakdown:")
    print("-" * 60)
    for store in proposal['stores']:
        if store['sold'] > 0:
            print(f"  {store['id']:3} {store['name']:20} Verkocht: {store['sold']:3}")
    print("-" * 60)
    print(f"  TOTAAL VERKOCHT: {total_verkocht}")
    print()
    
    # Step 5: Verify the result
    print("Step 5: Verification")
    print("=" * 60)
    
    EXPECTED_VERKOCHT = 50  # From the PDF
    
    if total_verkocht == EXPECTED_VERKOCHT:
        print(f"✅ SUCCESS! Verkocht totaal is correct: {total_verkocht}")
        print(f"   Expected: {EXPECTED_VERKOCHT}")
        print(f"   Actual:   {total_verkocht}")
        print()
        print("🎉 The fix works! Verkocht is no longer duplicated per maat.")
        return True
    else:
        print(f"❌ FAILED! Verkocht totaal is incorrect!")
        print(f"   Expected: {EXPECTED_VERKOCHT}")
        print(f"   Actual:   {total_verkocht}")
        print(f"   Difference: {total_verkocht - EXPECTED_VERKOCHT}")
        
        if total_verkocht == 450:
            print()
            print("   This is the OLD bug value (9x too high)")
            print("   The fix was not applied correctly.")
        
        return False

if __name__ == "__main__":
    try:
        success = test_verkocht_totaal()
        print()
        print("=" * 60)
        if success:
            print("TEST PASSED ✅")
        else:
            print("TEST FAILED ❌")
        print("=" * 60)
    except Exception as e:
        print(f"❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
