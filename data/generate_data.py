"""
Generate QA dataset for Retail AI Assistant.
Creates realistic Q&A pairs for 4 major departments:
- HR (Internal)
- IT Support (Internal)
- Billing & Payments (External)
- Shipping & Delivery (External)
"""

import json
from pathlib import Path
from typing import List, Dict, Any


def generate_hr_faqs() -> List[Dict[str, Any]]:
    """Generate HR department FAQs for internal employees."""
    faqs = [
        {
            "doc": "Q: What is the company holiday schedule for 2025?\nA: Our 2025 holiday schedule includes: New Year's Day (Jan 1), MLK Day (Jan 20), Presidents Day (Feb 17), Memorial Day (May 26), Independence Day (Jul 4), Labor Day (Sep 1), Thanksgiving (Nov 27-28), and Christmas (Dec 25). Additional time off can be requested through the employee portal.",
            "category": "HR",
            "audience": "internal"
        },
        {
            "doc": "Q: How do I request time off or PTO?\nA: You can request PTO through the HR Management System on the employee portal. Submit your request at least 2 weeks in advance for standard requests. Your manager will receive a notification and must approve within 3 business days. Emergency time off can be requested directly to your manager.",
            "category": "HR",
            "audience": "internal"
        },
        {
            "doc": "Q: What is the company's remote work policy?\nA: We offer a flexible hybrid work arrangement. Full-time employees can work remotely up to 3 days per week. Remote work approval requires manager consent and must not impact team collaboration. Core hours are 10 AM - 3 PM for video meetings.",
            "category": "HR",
            "audience": "internal"
        },
        {
            "doc": "Q: How are performance reviews conducted?\nA: Annual performance reviews occur in January. You'll receive a self-assessment form to complete. Your manager will conduct a one-on-one meeting and provide feedback based on goals, competencies, and contributions. Reviews determine salary adjustments and promotion eligibility.",
            "category": "HR",
            "audience": "internal"
        },
        {
            "doc": "Q: What health insurance options are available?\nA: We offer three health insurance plans: Bronze (low cost, higher deductible), Silver (balanced coverage), and Gold (comprehensive coverage). Dental and vision coverage are included. Open enrollment occurs in November for January coverage. Dependents can be added at any time.",
            "category": "HR",
            "audience": "internal"
        },
        {
            "doc": "Q: What is the 401(k) matching program?\nA: The company matches 100% of employee contributions up to 3% of salary and 50% of contributions from 3-5%. Employees are immediately eligible to enroll. Vesting is 25% per year over 4 years. You can adjust contributions anytime through the benefits portal.",
            "category": "HR",
            "audience": "internal"
        },
        {
            "doc": "Q: How do I update my personal information (address, emergency contacts)?\nA: Log into the HR Management System on the employee portal and navigate to 'Profile' > 'Personal Information'. Update your details and click 'Save'. Changes are typically reflected in our systems within 24 hours. Contact HR for assistance if you need help.",
            "category": "HR",
            "audience": "internal"
        },
        {
            "doc": "Q: What professional development opportunities are available?\nA: We offer tuition reimbursement (up to $5,000/year), LinkedIn Learning access, industry certifications support, and internal training workshops. Submit requests to your manager for approval. We also sponsor attendance at relevant conferences annually.",
            "category": "HR",
            "audience": "internal"
        },
        {
            "doc": "Q: What is the parental leave policy?\nA: We offer 12 weeks of paid parental leave for all employees (birth parent or non-birth parent). Employees may use up to 4 additional weeks of unpaid leave. Benefits continue during leave. Return-to-work schedules are flexible and negotiable.",
            "category": "HR",
            "audience": "internal"
        },
        {
            "doc": "Q: How does the employee referral program work?\nA: Refer a candidate who is hired and receive a $2,000 bonus (paid after 90 days). Refer a manager-level or above and receive $3,000. Referred employees must remain employed for at least 6 months for bonus payment.",
            "category": "HR",
            "audience": "internal"
        },
        {
            "doc": "Q: What should I do if I experience workplace harassment or discrimination?\nA: Report it immediately to HR or use our anonymous ethics hotline: 1-800-ETHICS-1. Investigations are confidential and conducted within 10 business days. We have zero tolerance for retaliation and have multiple reporting channels available.",
            "category": "HR",
            "audience": "internal"
        },
        {
            "doc": "Q: How is overtime calculated and compensated?\nA: Hourly employees receive 1.5x pay for hours over 40/week. Salaried exempt employees don't receive overtime pay but can take compensatory time off if required to work extended hours. Overtime must be pre-approved by your manager.",
            "category": "HR",
            "audience": "internal"
        },
        {
            "doc": "Q: What is the dress code policy?\nA: We maintain a business casual dress code: collared shirts, khakis/business pants for most departments. Client-facing roles may require business formal. No jeans, athletic wear, or visible tattoos/piercings. Casual Fridays allow jeans with company-branded items.",
            "category": "HR",
            "audience": "internal"
        },
        {
            "doc": "Q: How do I enroll in company wellness programs?\nA: Visit the Wellness Portal through the HR Management System. We offer fitness center subsidies ($50/month reimbursement), mental health counseling (EAP), nutrition coaching, and wellness challenges with prizes. Enrollment is free and open year-round.",
            "category": "HR",
            "audience": "internal"
        },
        {
            "doc": "Q: What happens during the onboarding process for new employees?\nA: New hires receive welcome materials, IT equipment setup, security badge creation, and attend a company overview session. Your manager schedules team introductions and training on role-specific systems. Full onboarding typically takes 2-3 weeks with regular check-ins.",
            "category": "HR",
            "audience": "internal"
        }
    ]
    return faqs


def generate_it_support_faqs() -> List[Dict[str, Any]]:
    """Generate IT Support department FAQs for internal employees."""
    faqs = [
        {
            "doc": "Q: How do I reset my password?\nA: Go to https://support.company.com/password-reset and enter your email. You'll receive a reset link valid for 24 hours. If you don't receive it, check your spam folder or contact IT support at extension 5555. Password must be at least 12 characters with mixed case and symbols.",
            "category": "IT Support",
            "audience": "internal"
        },
        {
            "doc": "Q: How do I connect to the VPN from home?\nA: Download and install Cisco AnyConnect VPN client from IT Portal. Launch the app, enter 'vpn.company.com', and log in with your employee credentials. Once connected, you have full network access. Contact IT if you experience connection issues.",
            "category": "IT Support",
            "audience": "internal"
        },
        {
            "doc": "Q: What do I do if my laptop won't turn on?\nA: First, check if the power adapter is plugged in properly. Wait 30 seconds and try again. If still unresponsive, hold the power button for 10 seconds. Contact IT Help Desk at x5555 or submit a ticket at support.company.com. They can arrange repairs or replacement.",
            "category": "IT Support",
            "audience": "internal"
        },
        {
            "doc": "Q: How do I access shared files and folders?\nA: Access shared drives through File Explorer (Windows) or Finder (Mac) using your employee credentials. Team folders are on the S: drive. You can also use OneDrive for personal file storage (1TB limit). Contact your manager if you need access to specific folders.",
            "category": "IT Support",
            "audience": "internal"
        },
        {
            "doc": "Q: How do I request software installation?\nA: Submit a request through the IT Portal under 'Software Requests'. Include the software name, version, and business justification. IT evaluates for security and licensing. Approval usually takes 5 business days. Company-approved software is free; other requests may incur costs.",
            "category": "IT Support",
            "audience": "internal"
        },
        {
            "doc": "Q: What is the company's data security policy?\nA: Never share passwords via email. Encrypt sensitive documents. Lock your laptop when stepping away. Don't use public WiFi for company work. Report security breaches immediately. Violation of data security policies can result in termination. Security training is mandatory annually.",
            "category": "IT Support",
            "audience": "internal"
        },
        {
            "doc": "Q: How do I set up my email on my mobile device?\nA: Go to Settings > Mail > Add Account. Select 'Exchange' and enter your email/password. If it fails, contact IT to ensure mobile device management is enabled. Use the company mobile security app for added protection. Only use company devices for business emails.",
            "category": "IT Support",
            "audience": "internal"
        },
        {
            "doc": "Q: What should I do if I suspect a phishing email?\nA: Don't click any links or download attachments. Forward it to security@company.com with 'PHISHING' in subject line. Delete the email. IT will investigate and advise. Report any suspicious activity immediately. Clicking phishing links can compromise network security.",
            "category": "IT Support",
            "audience": "internal"
        },
        {
            "doc": "Q: How do I access the company intranet?\nA: Go to intranet.company.com and log in with your employee credentials. The intranet has company announcements, policies, directories, and resources. Bookmark it for frequent access. Contact IT if you can't log in or see an error message.",
            "category": "IT Support",
            "audience": "internal"
        },
        {
            "doc": "Q: What video conferencing platform do we use?\nA: We use Microsoft Teams for video conferencing. Download it from the IT Portal. Join meetings using the calendar invite links. You can also schedule meetings through Teams. For support during calls, contact IT Help Desk via phone.",
            "category": "IT Support",
            "audience": "internal"
        },
        {
            "doc": "Q: How do I get IT support outside business hours?\nA: During business hours (8 AM - 6 PM), call x5555 or use the IT Portal. After hours, call the IT On-Call number at 1-800-IT-HELP-1. For urgent security issues anytime, use the emergency hotline. Response time guaranteed within 4 hours for critical issues.",
            "category": "IT Support",
            "audience": "internal"
        },
        {
            "doc": "Q: What should I do with old company equipment before leaving?\nA: Submit an exit request through HR. IT will schedule equipment collection (laptop, monitor, phone, etc.). Back up personal files before collection. All equipment becomes company property. Failure to return equipment may delay final paycheck.",
            "category": "IT Support",
            "audience": "internal"
        },
        {
            "doc": "Q: How do I print to company printers from home?\nA: Print documents through the cloud print portal while on VPN. Log in at https://cloudprint.company.com. Select your home-enabled printer. Release the job at the office printer using your badge. Contact IT to enable home printing on your account.",
            "category": "IT Support",
            "audience": "internal"
        },
        {
            "doc": "Q: What are the system backup and disaster recovery procedures?\nA: All employee files on network drives are backed up automatically daily. Local device backups aren't guaranteed. Enable automatic OneDrive sync for critical files. In case of data loss, contact IT within 30 days for potential recovery. Backups are retained for 30 days.",
            "category": "IT Support",
            "audience": "internal"
        },
        {
            "doc": "Q: How do I update my monitor resolution or display settings?\nA: Right-click on your desktop and select 'Display Settings'. Adjust resolution and scaling as needed. For Mac, go to System Preferences > Displays. If you experience resolution issues, restart and contact IT. Dual monitor support is available upon request.",
            "category": "IT Support",
            "audience": "internal"
        }
    ]
    return faqs


def generate_billing_payments_faqs() -> List[Dict[str, Any]]:
    """Generate Billing & Payments FAQs for external customers."""
    faqs = [
        {
            "doc": "Q: What payment methods do you accept?\nA: We accept all major credit cards (Visa, MasterCard, American Express), debit cards, PayPal, Apple Pay, Google Pay, and bank transfers. For large orders, we offer payment plans through Affirm or Klarna. All payments are processed securely with 256-bit encryption.",
            "category": "Billing & Payments",
            "audience": "external"
        },
        {
            "doc": "Q: Is it safe to enter my credit card information on your website?\nA: Yes, our website uses industry-standard SSL encryption to protect your payment information. We comply with PCI DSS security standards. Your credit card information is never stored on our servers. We never share your payment details with third parties.",
            "category": "Billing & Payments",
            "audience": "external"
        },
        {
            "doc": "Q: How can I update my billing address?\nA: Log into your account and go to 'Account Settings' > 'Billing Address'. Update your information and click 'Save'. Changes take effect immediately for future orders. If you've already placed an order, contact customer service within 24 hours to modify the address.",
            "category": "Billing & Payments",
            "audience": "external"
        },
        {
            "doc": "Q: Do you offer discounts or promotional codes?\nA: Yes! Subscribe to our newsletter for exclusive discount codes. We offer seasonal promotions (10-25% off), bulk order discounts (5+ items), and loyalty rewards (1 point per $1 spent). Sign up for our rewards program at checkout for immediate 10% off.",
            "category": "Billing & Payments",
            "audience": "external"
        },
        {
            "doc": "Q: Can I use multiple promo codes on one order?\nA: No, only one promo code can be applied per order. The system automatically applies the code with the highest discount value. Coupon codes have specific terms (expiration dates, minimum purchase amounts, product restrictions). Check code details before applying.",
            "category": "Billing & Payments",
            "audience": "external"
        },
        {
            "doc": "Q: How long does it take to process a refund?\nA: Once we receive and process your return, refunds are issued within 5-7 business days. The refund goes back to the original payment method. Shipping costs are non-refundable unless the item arrived damaged. You can track refund status in your account.",
            "category": "Billing & Payments",
            "audience": "external"
        },
        {
            "doc": "Q: What is your return policy and timeframe?\nA: We offer 30-day returns on most items in original, unused condition with original packaging. Initiate returns through your account or contact customer service. Clothing and electronics have specific return requirements. Refunds minus shipping are issued 5-7 days after we receive the item.",
            "category": "Billing & Payments",
            "audience": "external"
        },
        {
            "doc": "Q: Can I change my order after placing it?\nA: If your order hasn't shipped yet, contact us within 1 hour of purchase to make changes. Provide your order number and desired modifications. If the order has already shipped, you'll need to refuse delivery or initiate a return. Contact our support team immediately.",
            "category": "Billing & Payments",
            "audience": "external"
        },
        {
            "doc": "Q: Why was my payment declined?\nA: Common reasons include: insufficient funds, expired card, incorrect CVV, address mismatch, or fraud detection. Check your card details and try again. Contact your bank to ensure the card isn't blocked for online purchases. Try a different payment method if the issue persists.",
            "category": "Billing & Payments",
            "audience": "external"
        },
        {
            "doc": "Q: Do you charge sales tax?\nA: Yes, sales tax is calculated based on your shipping address and applicable local rates. Tax is added to your total at checkout. Some items may be tax-exempt depending on your location. We automatically handle all sales tax compliance for you.",
            "category": "Billing & Payments",
            "audience": "external"
        },
        {
            "doc": "Q: Can I get an invoice for my purchase?\nA: Invoices are automatically sent to your email after purchase. You can also access them anytime by logging into your account under 'Order History'. View, download, or print invoices in PDF format. Contact support if you don't receive your invoice.",
            "category": "Billing & Payments",
            "audience": "external"
        },
        {
            "doc": "Q: What is your billing cycle for subscriptions?\nA: Subscriptions renew automatically every month (or selected period) on your billing date. You can view your next billing date and manage subscriptions in your account settings. Cancel anytime before the renewal date with no penalties. We'll send a reminder email 3 days before renewal.",
            "category": "Billing & Payments",
            "audience": "external"
        },
        {
            "doc": "Q: How do I cancel my subscription?\nA: Go to 'Account Settings' > 'Subscriptions' and click 'Cancel'. You can select your cancellation reason. Your current plan remains active through the billing period. No refunds are issued for the current billing cycle, but cancellation is effective immediately.",
            "category": "Billing & Payments",
            "audience": "external"
        },
        {
            "doc": "Q: Are there any hidden fees?\nA: No hidden fees! All costs are clearly displayed before checkout: product price, shipping, tax, and any applicable fees. The final total in your invoice matches what you approved at checkout. We clearly separate all charges in your order confirmation.",
            "category": "Billing & Payments",
            "audience": "external"
        },
        {
            "doc": "Q: Can I request an invoice for bulk or business orders?\nA: Absolutely! For orders over $5,000, we offer business invoicing, net-30 payment terms, and volume discounts. Contact our business sales team at business@company.com with your order details. They'll provide a custom quote and invoice options.",
            "category": "Billing & Payments",
            "audience": "external"
        }
    ]
    return faqs


def generate_shipping_delivery_faqs() -> List[Dict[str, Any]]:
    """Generate Shipping & Delivery FAQs for external customers."""
    faqs = [
        {
            "doc": "Q: How long does standard shipping take?\nA: Standard shipping typically takes 5-7 business days from order placement. Weekends and holidays are excluded. You'll receive a tracking number via email once your order ships. Orders placed before 2 PM ship the next business day. Track your package anytime using your tracking number.",
            "category": "Shipping & Delivery",
            "audience": "external"
        },
        {
            "doc": "Q: What are your shipping options?\nA: We offer: Standard (5-7 days, free on orders $50+), Express (2-3 days, $15), Overnight (1 day, $30). Weekend delivery available in select areas. For international orders, see our global shipping page. Select shipping speed at checkout. Rates calculated based on weight and destination.",
            "category": "Shipping & Delivery",
            "audience": "external"
        },
        {
            "doc": "Q: Do you offer free shipping?\nA: Free standard shipping on orders $50 and above within the continental US. Express and overnight shipping are additional charges. Sign up for our Prime membership ($99/year) for free 2-day shipping on all orders. Free shipping applies only to regular-sized items.",
            "category": "Shipping & Delivery",
            "audience": "external"
        },
        {
            "doc": "Q: Can I track my order?\nA: Yes! You'll receive a tracking number via email when your order ships. Use it on our tracking page or the carrier's website (USPS, UPS, FedEx). Orders ship within 24 hours. You can also track from your account dashboard in real-time. Tracking updates every 24 hours.",
            "category": "Shipping & Delivery",
            "audience": "external"
        },
        {
            "doc": "Q: Can I change my shipping address after placing an order?\nA: Contact us within 1 hour of placing your order with the new address. If your order has already shipped, you cannot change the address. You'll need to refuse delivery or initiate a return. For future orders, you can always update addresses at checkout.",
            "category": "Shipping & Delivery",
            "audience": "external"
        },
        {
            "doc": "Q: What do I do if my package arrives damaged?\nA: Document the damage with photos immediately. Contact customer service within 48 hours with your order number and photos. We'll arrange a replacement or refund. Most damaged items are shipped next day. Keep the damaged item and packaging for inspection if requested.",
            "category": "Shipping & Delivery",
            "audience": "external"
        },
        {
            "doc": "Q: What happens if my package is lost?\nA: We monitor all shipments. If tracking shows no delivery after 10 days, contact customer service with your tracking number. We'll file a claim with the carrier and send a replacement or issue a refund. Carrier liability is up to $100 for basic shipping.",
            "category": "Shipping & Delivery",
            "audience": "external"
        },
        {
            "doc": "Q: Can I require a signature on delivery?\nA: Yes, you can add signature confirmation at checkout. This ensures someone is home to receive it. Adds 1-2 days to delivery time. Signature confirmation is automatically required for orders over $500. Required signatures increase shipping cost by $5.",
            "category": "Shipping & Delivery",
            "audience": "external"
        },
        {
            "doc": "Q: Do you ship internationally?\nA: Yes! We ship to 50+ countries. International shipping typically takes 10-14 business days. Customers are responsible for import duties and taxes (calculated at destination). Tracking is available for all international orders. Check your country's import restrictions before ordering.",
            "category": "Shipping & Delivery",
            "audience": "external"
        },
        {
            "doc": "Q: What is your packaging and sustainability policy?\nA: We use recyclable and compostable materials whenever possible. All boxes are made from 100% recycled cardboard. Plastic fillers are biodegradable. We're carbon-neutral for all shipping within the US. Choose eco-friendly shipping to offset carbon emissions (minimal cost).",
            "category": "Shipping & Delivery",
            "audience": "external"
        },
        {
            "doc": "Q: Can I hold my package for pickup at a location?\nA: Yes, select 'Pickup Point' at checkout. Choose from 500+ locations nationwide. Your order ships to your selected location (1-2 extra days). Pick up within 7 days of arrival notification. Valid ID is required. Pickup points are available at select retailers.",
            "category": "Shipping & Delivery",
            "audience": "external"
        },
        {
            "doc": "Q: How do I arrange a return shipment?\nA: Orders within 30 days can be returned. Request a return label through your account (free label provided). Package your item securely and drop off at any carrier location. Include your return authorization number. Refunds processed 5-7 days after receipt.",
            "category": "Shipping & Delivery",
            "audience": "external"
        },
        {
            "doc": "Q: What should I do if my delivery is delayed?\nA: Check your tracking for current status. Delays happen for weather, carrier issues, or high volume. Contact customer service if more than 5 days late. We'll investigate and offer a 10% discount on your next order. Extreme delays may result in refund or replacement.",
            "category": "Shipping & Delivery",
            "audience": "external"
        },
        {
            "doc": "Q: Can I schedule a specific delivery time?\nA: We offer delivery time windows (morning 8-12, afternoon 12-5, or evening 5-8) for express and overnight shipping. Choose your preferred window at checkout. Exact time cannot be guaranteed due to carrier scheduling. Standard shipping is delivered whenever the carrier arrives.",
            "category": "Shipping & Delivery",
            "audience": "external"
        },
        {
            "doc": "Q: What are your holiday shipping cutoff dates?\nA: Christmas: order by Dec 18 (standard), Dec 22 (express). New Year: order by Dec 30 (standard), Jan 1 (express). Thanksgiving: order by Nov 19 (standard), Nov 24 (express). All times are 2 PM EST. Holiday schedules posted on our shipping page 60 days in advance.",
            "category": "Shipping & Delivery",
            "audience": "external"
        }
    ]
    return faqs


def save_dataset(faqs: List[Dict[str, Any]], filepath: str) -> None:
    """Save the QA dataset to a JSON file."""
    output_path = Path(filepath)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(faqs, f, indent=2, ensure_ascii=False)

    print(f"✓ Dataset saved to {filepath}")
    print(f"✓ Total Q&A pairs: {len(faqs)}")
    print(f"✓ File size: {output_path.stat().st_size / 1024:.2f} KB")


def main():
    """Generate and save the complete QA dataset."""
    print("\n" + "="*70)
    print("QA Dataset Generator for Retail AI Assistant")
    print("="*70 + "\n")

    # Generate FAQs for all departments
    print("Generating FAQs for all departments...\n")

    print("► HR Department (Internal Employees)...")
    hr_faqs = generate_hr_faqs()
    print(f"  Generated {len(hr_faqs)} Q&A pairs")

    print("► IT Support Department (Internal Employees)...")
    it_faqs = generate_it_support_faqs()
    print(f"  Generated {len(it_faqs)} Q&A pairs")

    print("► Billing & Payments Department (External Customers)...")
    billing_faqs = generate_billing_payments_faqs()
    print(f"  Generated {len(billing_faqs)} Q&A pairs")

    print("► Shipping & Delivery Department (External Customers)...")
    shipping_faqs = generate_shipping_delivery_faqs()
    print(f"  Generated {len(shipping_faqs)} Q&A pairs")

    # Combine all FAQs
    all_faqs = hr_faqs + it_faqs + billing_faqs + shipping_faqs

    print(f"\n{'─'*70}")
    print(f"Total Q&A pairs generated: {len(all_faqs)}")
    print(f"Department breakdown:")
    print(f"  • HR: {len(hr_faqs)}")
    print(f"  • IT Support: {len(it_faqs)}")
    print(f"  • Billing & Payments: {len(billing_faqs)}")
    print(f"  • Shipping & Delivery: {len(shipping_faqs)}")
    print(f"{'─'*70}\n")

    # Save to JSON
    filepath = "data/synthetic_datasets.json"
    save_dataset(all_faqs, filepath)

    print("\n✓ Dataset generation complete!")
    print(f"✓ Location: {filepath}")
    print("\nDataset structure:")
    print("  - Each entry contains:")
    print("    • doc: Formatted Q&A pair")
    print("    • category: Department name")
    print("    • audience: 'internal' or 'external'")
    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    main()
