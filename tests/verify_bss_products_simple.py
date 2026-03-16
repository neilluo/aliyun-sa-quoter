"""Simple verification of BSS product configurations.

Requires environment variables:
  ALIBABA_CLOUD_ACCESS_KEY_ID
  ALIBABA_CLOUD_ACCESS_KEY_SECRET
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "skill" / "scripts"))

from bss_client import create_client, _call_api

client = create_client()
ak, sk = client

products = [
    ("Redis", "redisa", ""),
    ("PolarDB", "polardb", "online"),
    ("MongoDB", "dds", ""),
]

print("="*60)
print("BSS Products Configuration Verification")
print("="*60)

all_pass = True
for name, code, ptype in products:
    print(f"\nTesting {name} (Code: {code}, Type: '{ptype}')...")
    
    params = {
        "ProductCode": code,
        "SubscriptionType": "Subscription",
    }
    if ptype:
        params["ProductType"] = ptype
    
    try:
        body = _call_api("DescribePricingModule", params, ak, sk)
        if body.get("Success"):
            modules = body.get("Data", {}).get("ModuleList", {}).get("Module", [])
            print(f"  ✓ PASS - Found {len(modules)} modules")
        else:
            print(f"  ✗ FAIL - {body.get('Message')}")
            all_pass = False
    except Exception as e:
        print(f"  ✗ FAIL - {e}")
        all_pass = False

print("\n" + "="*60)
if all_pass:
    print("✓ All products verified successfully!")
    sys.exit(0)
else:
    print("✗ Some verifications failed.")
    sys.exit(1)
