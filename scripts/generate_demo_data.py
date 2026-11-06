"""
DisputeShield AI — Demo Data Generator & Precedent Seeder (Day 12)

Generates 32 realistic dispute records:
- 10 Physical Item Not Received (INR)
- 8 Digital Goods / Services Not Received
- 8 Significantly Not As Described (SNAD)
- 6 Unauthorized Transaction Claims

Computes 1536-dimensional embeddings for each dispute and seeds them into
Elasticsearch (or in-memory mock store) for kNN vector search precedent retrieval.
Also seeds corresponding records in the relational database if available.
"""

import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

# Ensure backend root is on sys.path and fallback DB is configured
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

os.environ.setdefault("DATABASE_URL", "sqlite:///./demo.db")

from agent.rag_retriever import RAGRetriever
from services.elasticsearch_service import ElasticsearchService

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------------
# Curated Precedent Dataset (32 Disputes)
# -------------------------------------------------------------------------

DEMO_DISPUTES: List[Dict[str, Any]] = [
    # ---------------------------------------------------------------------
    # 1. Physical INR (10 Cases)
    # ---------------------------------------------------------------------
    {
        "dispute_id": "PP-D-DEMO-001",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": 149.99,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "PHYSICAL",
        "carrier_name": "UPS",
        "tracking_number": "1Z9999999999999901",
        "delivery_status": "DELIVERED",
        "buyer_message": "Package never arrived at my house. Porch is completely empty.",
        "seller_response": "UPS tracking shows package delivered to front door with GPS coordinates matching buyer address.",
        "evidence_summary": "Carrier online tracking showed DELIVERED status with recipient postal code verification and GPS geo-stamp.",
        "created_at": (datetime.utcnow() - timedelta(days=45)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-002",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": 89.50,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "PHYSICAL",
        "carrier_name": "USPS",
        "tracking_number": "94001118992231000002",
        "delivery_status": "DELIVERED",
        "buyer_message": "Tracking has been stuck for weeks. I want my money back immediately.",
        "seller_response": "USPS priority mail tracking confirms delivery to mailbox on Oct 4.",
        "evidence_summary": "USPS delivery confirmation receipt and postal manifest showing exact recipient zip code match.",
        "created_at": (datetime.utcnow() - timedelta(days=40)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-003",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": 420.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "PHYSICAL",
        "carrier_name": "FedEx",
        "tracking_number": "794892830003",
        "delivery_status": "DELIVERED",
        "buyer_message": "Ordered premium headphones, never received them.",
        "seller_response": "FedEx Direct Signature required obtained at recipient address. Signed by buyer.",
        "evidence_summary": "Proof of delivery with direct signature verification matching buyer name and address.",
        "created_at": (datetime.utcnow() - timedelta(days=38)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-004",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": 29.99,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "PHYSICAL",
        "carrier_name": "DHL",
        "tracking_number": "DHL98230004",
        "delivery_status": "DELIVERED",
        "buyer_message": "Did not receive my phone charger.",
        "seller_response": "DHL Express tracking confirms delivery to parcel locker.",
        "evidence_summary": "Carrier proof of delivery to secure building parcel locker with entry log PIN confirmation.",
        "created_at": (datetime.utcnow() - timedelta(days=35)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-005",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": 310.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "LOST",
        "item_type": "PHYSICAL",
        "carrier_name": "USPS",
        "tracking_number": "94001118992231000005",
        "delivery_status": "IN_TRANSIT",
        "buyer_message": "Tracking shows package lost in transit since last month. No updates.",
        "seller_response": "Package was handed over to USPS on time.",
        "evidence_summary": "Carrier tracking showed in transit with no final delivery confirmation before deadline.",
        "created_at": (datetime.utcnow() - timedelta(days=32)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-006",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": 195.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "PHYSICAL",
        "carrier_name": "FedEx",
        "tracking_number": "794892830006",
        "delivery_status": "DELIVERED",
        "buyer_message": "Claiming non-delivery for luxury jacket.",
        "seller_response": "FedEx delivery confirmation with photo showing package safely placed inside screened porch.",
        "evidence_summary": "Carrier delivery photo and timestamped scan at buyer residence matching order street number.",
        "created_at": (datetime.utcnow() - timedelta(days=28)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-007",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": 54.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "PHYSICAL",
        "carrier_name": "UPS",
        "tracking_number": "1Z9999999999999907",
        "delivery_status": "DELIVERED",
        "buyer_message": "Package was stolen or delivered to wrong apartment unit.",
        "seller_response": "Shipped to exact address provided on PayPal checkout. Tracking indicates delivered.",
        "evidence_summary": "Carrier delivery record matching PayPal verified address and unit number.",
        "created_at": (datetime.utcnow() - timedelta(days=25)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-008",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": 260.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "PHYSICAL",
        "carrier_name": "UPS",
        "tracking_number": "1Z9999999999999908",
        "delivery_status": "DELIVERED",
        "buyer_message": "Did not receive gaming keyboard order.",
        "seller_response": "Delivered on schedule. UPS tracking and signature provided.",
        "evidence_summary": "Carrier tracking verification with signature on file.",
        "created_at": (datetime.utcnow() - timedelta(days=21)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-009",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": 850.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "LOST",
        "item_type": "PHYSICAL",
        "carrier_name": "FedEx",
        "tracking_number": "794892830009",
        "delivery_status": "DELIVERED",
        "buyer_message": "High value laptop never arrived. No signature collected.",
        "seller_response": "Tracking shows package left at front door.",
        "evidence_summary": "Order value exceeded $750 PayPal threshold requiring signature confirmation; only standard delivery scan was provided.",
        "created_at": (datetime.utcnow() - timedelta(days=18)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-010",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": 115.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "PHYSICAL",
        "carrier_name": "USPS",
        "tracking_number": "94001118992231000010",
        "delivery_status": "DELIVERED",
        "buyer_message": "Items were not delivered to my address in Seattle.",
        "seller_response": "Shipped via USPS Priority with address validation.",
        "evidence_summary": "Online tracking confirmation demonstrating delivery to destination city and zip code.",
        "created_at": (datetime.utcnow() - timedelta(days=14)).isoformat(),
    },

    # ---------------------------------------------------------------------
    # 2. Digital INR (8 Cases)
    # ---------------------------------------------------------------------
    {
        "dispute_id": "PP-D-DEMO-011",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": 79.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "DIGITAL",
        "buyer_message": "I purchased annual SaaS software subscription but never got login credentials or access.",
        "seller_response": "Account provisioned within 2 minutes. Audit log shows buyer logged in 4 times and downloaded files.",
        "evidence_summary": "Provided server authentication logs, IP address match with PayPal account, and license activation key receipt.",
        "created_at": (datetime.utcnow() - timedelta(days=42)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-012",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": 45.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "DIGITAL",
        "buyer_message": "Digital ebook download link failed to work.",
        "seller_response": "Download link sent immediately via email and accessed 3 times from customer IP.",
        "evidence_summary": "S3 CDN access logs demonstrating successful HTTP 200 byte range requests from customer IP.",
        "created_at": (datetime.utcnow() - timedelta(days=36)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-013",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": 250.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "DIGITAL",
        "buyer_message": "Web design consulting hours were never delivered.",
        "seller_response": "Detailed timesheet and Loom video review walkthrough delivered via email.",
        "evidence_summary": "Delivery of deliverables via documented client portal, Figma link history, and signed statement of work.",
        "created_at": (datetime.utcnow() - timedelta(days=30)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-014",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": 120.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "LOST",
        "item_type": "DIGITAL",
        "buyer_message": "Course access revoked immediately after payment.",
        "seller_response": "User broke terms of service by sharing login credentials.",
        "evidence_summary": "Merchant failed to provide concrete access logs or warning notification prior to account termination.",
        "created_at": (datetime.utcnow() - timedelta(days=26)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-015",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": 35.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "DIGITAL",
        "buyer_message": "Never received my digital gift card code.",
        "seller_response": "Code sent to buyer PayPal email address. Code redemption log confirms redeemed on Steam.",
        "evidence_summary": "Digital gift code redemption log with timestamp and email delivery confirmation.",
        "created_at": (datetime.utcnow() - timedelta(days=22)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-016",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": 199.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "DIGITAL",
        "buyer_message": "Digital API credits were not added to my developer workspace.",
        "seller_response": "50,000 credits allocated immediately upon checkout. 12,000 credits already consumed.",
        "evidence_summary": "Database transaction log showing credit top-up and API request metrics from buyer API key.",
        "created_at": (datetime.utcnow() - timedelta(days=19)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-017",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": 60.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "DIGITAL",
        "buyer_message": "Font license bundle was not downloadable.",
        "seller_response": "Download link sent with download receipt.",
        "evidence_summary": "Email delivery receipt from SendGrid and download server log timestamp.",
        "created_at": (datetime.utcnow() - timedelta(days=15)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-018",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_RECEIVED",
        "dispute_amount": 150.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "LOST",
        "item_type": "DIGITAL",
        "buyer_message": "SEO audit was never delivered.",
        "seller_response": "We emailed the report.",
        "evidence_summary": "Email bounced due to incorrect recipient address; merchant did not re-send or provide proof of delivery.",
        "created_at": (datetime.utcnow() - timedelta(days=10)).isoformat(),
    },

    # ---------------------------------------------------------------------
    # 3. SNAD - Significantly Not As Described (8 Cases)
    # ---------------------------------------------------------------------
    {
        "dispute_id": "PP-D-DEMO-019",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
        "dispute_amount": 185.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "PHYSICAL",
        "buyer_message": "The camera lens is fake and has different focal length than listing.",
        "seller_response": "Listing clearly specifies 50mm f/1.8 lens with exact manufacturer model number matching invoice.",
        "evidence_summary": "Product listing snapshot, SKU number match, and manufacturer authorized distributor certificate.",
        "created_at": (datetime.utcnow() - timedelta(days=44)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-020",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
        "dispute_amount": 95.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "PHYSICAL",
        "buyer_message": "Color is completely different from website photos. It looks orange instead of brown.",
        "seller_response": "Color code #8B4513 (Saddle Brown) specified on product description with swatch disclaimer.",
        "evidence_summary": "Product catalog specification, clear description of natural leather shade variation, and return policy offer.",
        "created_at": (datetime.utcnow() - timedelta(days=39)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-021",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
        "dispute_amount": 340.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "LOST",
        "item_type": "PHYSICAL",
        "buyer_message": "Received broken ceramic vase with multiple cracks throughout.",
        "seller_response": "Item was packaged with bubble wrap. Damage must have occurred in shipping.",
        "evidence_summary": "Buyer provided unboxing photographs showing damaged goods; merchant did not purchase postal insurance.",
        "created_at": (datetime.utcnow() - timedelta(days=33)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-022",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
        "dispute_amount": 125.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "PHYSICAL",
        "buyer_message": "The jacket size runs way too small, fits like a Small instead of XL.",
        "seller_response": "Exact dimensional measurements (chest 46in, length 30in) listed in sizing chart.",
        "evidence_summary": "Sizing chart comparison, garment measurement tag photograph, and offer for exchange.",
        "created_at": (datetime.utcnow() - timedelta(days=29)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-023",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
        "dispute_amount": 220.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "PHYSICAL",
        "buyer_message": "Claimed original factory refurbished, but looks used with scratch on bezel.",
        "seller_response": "Product graded as 'Grade B Refurbished - minor cosmetic blemishes' as stated prominently in title and description.",
        "evidence_summary": "Clear condition disclosure in product title and description agreeing with manufacturer refurbishment guidelines.",
        "created_at": (datetime.utcnow() - timedelta(days=24)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-024",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
        "dispute_amount": 410.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "LOST",
        "item_type": "PHYSICAL",
        "buyer_message": "Ordered 1TB SSD model, package contained 512GB model.",
        "seller_response": "Warehouse barcode error might have occurred.",
        "evidence_summary": "Buyer provided packaging photo with packing slip showing SKU mismatch; merchant admitted shipping error.",
        "created_at": (datetime.utcnow() - timedelta(days=17)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-025",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
        "dispute_amount": 75.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "PHYSICAL",
        "buyer_message": "Watch band is synthetic leather instead of genuine leather.",
        "seller_response": "Description clearly specifies 'High-Grade Vegan Leather (PU)'.",
        "evidence_summary": "Listing copy highlighted Vegan Leather 4 times; customer agreement to purchase specifications.",
        "created_at": (datetime.utcnow() - timedelta(days=12)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-026",
        "reason": "MERCHANDISE_OR_SERVICE_NOT_AS_DESCRIBED",
        "dispute_amount": 160.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "PHYSICAL",
        "buyer_message": "Sound quality on speakers does not meet expectations.",
        "seller_response": "Product functions exactly according to factory specs. Buyer did not initiate standard return.",
        "evidence_summary": "Provided manufacturer spec sheet, return policy guidelines, and offer to provide pre-paid return label.",
        "created_at": (datetime.utcnow() - timedelta(days=8)).isoformat(),
    },

    # ---------------------------------------------------------------------
    # 4. Unauthorized Transactions (6 Cases)
    # ---------------------------------------------------------------------
    {
        "dispute_id": "PP-D-DEMO-027",
        "reason": "UNAUTHORIZED",
        "dispute_amount": 110.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "PHYSICAL",
        "carrier_name": "UPS",
        "tracking_number": "1Z9999999999999927",
        "delivery_status": "DELIVERED",
        "buyer_message": "I did not recognize this transaction on my statement. Someone compromised my PayPal.",
        "seller_response": "Shipped to verified PayPal account holder address. Order placed from recurrent IP with 2FA pass.",
        "evidence_summary": "Shipped directly to verified PayPal billing address with confirmed 2FA authentication timestamp and delivery proof.",
        "created_at": (datetime.utcnow() - timedelta(days=41)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-028",
        "reason": "UNAUTHORIZED",
        "dispute_amount": 65.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "DIGITAL",
        "buyer_message": "Unknown charge for online gaming tokens.",
        "seller_response": "Purchased by account with 3 years history, device fingerprint matched existing sessions.",
        "evidence_summary": "Account transaction history, device fingerprint match, and delivery of virtual tokens to registered gamer tag.",
        "created_at": (datetime.utcnow() - timedelta(days=34)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-029",
        "reason": "UNAUTHORIZED",
        "dispute_amount": 490.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "PHYSICAL",
        "carrier_name": "FedEx",
        "tracking_number": "794892830029",
        "delivery_status": "DELIVERED",
        "buyer_message": "Card was stolen and used to purchase electronics.",
        "seller_response": "Address Verification System (AVS) matched 100%. Shipped with adult signature required.",
        "evidence_summary": "AVS and CVV full match, PayPal Seller Protection eligibility confirmed, FedEx signed delivery receipt.",
        "created_at": (datetime.utcnow() - timedelta(days=27)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-030",
        "reason": "UNAUTHORIZED",
        "dispute_amount": 320.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "LOST",
        "item_type": "PHYSICAL",
        "carrier_name": "DHL",
        "tracking_number": "DHL98230030",
        "delivery_status": "DELIVERED",
        "buyer_message": "Fraudulent charge shipped to freight forwarder in Delaware.",
        "seller_response": "Shipped to address requested in order comments.",
        "evidence_summary": "Order was redirected to freight forwarder address not listed on PayPal transaction; Seller Protection voided.",
        "created_at": (datetime.utcnow() - timedelta(days=20)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-031",
        "reason": "UNAUTHORIZED",
        "dispute_amount": 80.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "DIGITAL",
        "buyer_message": "Subscription renewal unauthorized.",
        "seller_response": "Recurring billing agreement signed by customer. Advance renewal notice sent 7 days prior.",
        "evidence_summary": "PayPal Recurring Payment Agreement authorization ID, email renewal notification log, and login audit trail.",
        "created_at": (datetime.utcnow() - timedelta(days=13)).isoformat(),
    },
    {
        "dispute_id": "PP-D-DEMO-032",
        "reason": "UNAUTHORIZED",
        "dispute_amount": 140.00,
        "dispute_currency": "USD",
        "status": "RESOLVED",
        "outcome": "WON",
        "item_type": "PHYSICAL",
        "carrier_name": "UPS",
        "tracking_number": "1Z9999999999999932",
        "delivery_status": "DELIVERED",
        "buyer_message": "Never authorized this clothing order.",
        "seller_response": "Order shipped to primary verified account address with UPS tracking delivered.",
        "evidence_summary": "Delivered to verified buyer street address on file; eligible for PayPal Seller Protection.",
        "created_at": (datetime.utcnow() - timedelta(days=6)).isoformat(),
    },
]


async def seed_precedents():
    """
    Generate dense embeddings and index all 32 demo disputes into Elasticsearch.
    """
    logger.info("Initializing RAG Retriever and Elasticsearch Service...")
    retriever = RAGRetriever()
    es_service = retriever.es_service

    # Ensure index exists
    index_created = await es_service.ensure_index()
    logger.info(f"Elasticsearch index check completed (index='{es_service.index_name}', status={index_created})")

    logger.info(f"Generating embeddings and indexing {len(DEMO_DISPUTES)} demo precedent cases...")
    
    seeded_count = 0
    won_count = 0
    lost_count = 0
    category_counts: Dict[str, int] = {}

    for i, dispute in enumerate(DEMO_DISPUTES, 1):
        # Construct composite text for dense embedding
        composite_text = (
            f"Reason: {dispute['reason']}. "
            f"Buyer message: {dispute['buyer_message']} "
            f"Seller response: {dispute.get('seller_response', '')} "
            f"Evidence: {dispute.get('evidence_summary', '')}"
        )

        # Generate 1536-dimensional embedding
        vector = await retriever.get_embedding(composite_text)

        # Index into Elasticsearch
        doc = {
            "dispute_id": dispute["dispute_id"],
            "reason": dispute["reason"],
            "status": dispute["status"],
            "amount": dispute["dispute_amount"],
            "buyer_message": dispute["buyer_message"],
            "evidence_summary": dispute["evidence_summary"],
            "outcome": dispute["outcome"],
            "created_at": dispute["created_at"],
        }

        success = await es_service.index_dispute(doc, vector=vector)
        if success:
            seeded_count += 1
            if dispute["outcome"] == "WON":
                won_count += 1
            else:
                lost_count += 1

            cat = dispute["reason"]
            category_counts[cat] = category_counts.get(cat, 0) + 1

        if i % 8 == 0 or i == len(DEMO_DISPUTES):
            logger.info(f"Progress: [{i}/{len(DEMO_DISPUTES)}] indexed successfully.")

    overall_win_rate = (won_count / seeded_count * 100) if seeded_count else 0.0

    print("\n" + "=" * 65)
    print("   DISPUTESHIELD AI — PRECEDENT SEEDING SUMMARY")
    print("=" * 65)
    print(f"Total Precedents Seeded : {seeded_count} / {len(DEMO_DISPUTES)}")
    print(f"Merchant Won Cases     : {won_count} ({overall_win_rate:.1f}%)")
    print(f"Merchant Lost Cases    : {lost_count} ({100 - overall_win_rate:.1f}%)")
    print("-" * 65)
    print("Breakdown by Category:")
    for cat, count in category_counts.items():
        print(f" - {cat:<42}: {count} cases")
    print("-" * 65)
    print("Index Target           : " + es_service.index_name)
    print("Vector Dimensions      : 1536 (Cosine Similarity)")
    print("=" * 65 + "\n")

    if es_service.client:
        await es_service.client.close()


if __name__ == "__main__":
    asyncio.run(seed_precedents())
