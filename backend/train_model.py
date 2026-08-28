import pandas as pd
import numpy as np
import os
import re
import joblib
from sklearn.model_selection import train_test_split, StratifiedKFold, cross_validate
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.pipeline import Pipeline, FeatureUnion
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, accuracy_score, precision_score, recall_score, f1_score, roc_auc_score

def create_dataset():
    """
    Generates an expanded, highly diverse dataset of 4,000+ labeled samples
    with real-world attack patterns, hard negatives (legitimate transactional/OTP messages),
    and diverse domain/URL structures.
    """
    np.random.seed(42)
    phishing_samples = []
    legitimate_samples = []

    # =========================================================================
    # 1. PHISHING TEMPLATES & COMPONENTS
    # =========================================================================
    phishing_domains = [
        # Typosquatting / Deceptive
        'paypal-security-update.xyz', 'paypal-verify-account.top', 'secure-paypal-login.club',
        'amazon-orders-support.click', 'amazon-prime-verify.xyz', 'amazon-account-locked.top',
        'appleid-verify-icloud.tk', 'apple-security-alert.ml', 'apple-support-auth.ga',
        'netflix-billing-renew.xyz', 'netflix-account-suspended.top', 'netflix-payment-info.club',
        'google-account-verify.cf', 'google-security-team.gq', 'google-drive-share.xyz',
        'microsoft-office365-login.net', 'office365-password-reset.click', 'microsoft-verify.top',
        'chase-online-banking.xyz', 'wellsfargo-secure-auth.club', 'bankofamerica-verify.ml',
        'citibank-account-update.top', 'sbi-card-reward.xyz', 'hdfc-kyc-update.online',
        'barclays-security-login.pw', 'hsbc-account-alert.xyz', 'coinbase-wallet-verify.net',
        'binance-airdrop-claim.top', 'metamask-restore-key.click', 'blockchain-wallet-login.xyz',
        'facebook-security-check.net', 'instagram-badge-verify.top', 'whatsapp-web-login.xyz',
        'linkedin-job-offer-apply.club', 'twitter-verification-badge.click',
        # IP based URLs
        '192.168.1.105', '10.0.0.84', '172.16.254.1', '198.51.100.23', '203.0.113.45',
        # Malicious / Spam TLDs
        'secure-login-gateway.xyz', 'urgent-action-required.top', 'account-verification-portal.buzz',
        'customer-support-desk.club', 'payment-gateway-update.work', 'online-service-portal.click',
        'cloud-drive-document.link', 'auth-verify-security.pw', 'member-service-center.icu',
        'direct-bonus-claim.fun', 'free-giftcard-offer.site', 'mobile-service-update.online'
    ]

    shorteners = ['bit.ly', 'tinyurl.com', 'is.gd', 't.co', 'cutt.ly', 'ow.ly', 'rb.gy']

    phishing_paths = [
        'login.php', 'verify-identity', 'update-billing', 'signin', 'account-suspended',
        'secure-auth', 'restore-access', 'claim-prize', 'confirm-details', 'tax-refund',
        'invoice/download', 'wallet/connect', 'document/view', 'reset-password', 'kyc/submit',
        'parcel/reschedule', 'support/ticket', 'security-checkpoint', 'billing/invoice.pdf.exe'
    ]

    # Category 1: Banking & Financial Phishing
    bank_phishing_templates = [
        "URGENT from {bank}: Your bank account has been temporarily restricted due to unauthorized login attempts. Verify immediately at http://{domain}/{path}",
        "Dear {bank} customer, your debit card is blocked. Unblock your card by updating your KYC at http://{domain}/{path}",
        "{bank} Alert: A transaction of $4,850.00 to CryptoExchange is pending. If this was not you, cancel it immediately: http://{domain}/{path}",
        "Important notification from {bank}: Unusual debit card activity detected. Confirm your identity to prevent permanent block: http://{domain}/{path}",
        "Your {bank} credit card rewards worth $450 are expiring today! Redeem your cashback now at http://{domain}/{path}",
        "{bank} Security Alert: Someone requested a password reset for your account. If you did not request this, secure your account: http://{domain}/{path}"
    ]
    banks = ['Chase Bank', 'Bank of America', 'Wells Fargo', 'Citibank', 'SBI', 'HDFC Bank', 'Barclays', 'HSBC', 'Capital One']

    # Category 2: Tech & Social Media Account Takeover
    tech_phishing_templates = [
        "Security Alert: Your {service} account password expires today. Keep your current password by verifying at http://{domain}/{path}",
        "Someone accessed your {service} account from Moscow, Russia. If this wasn't you, secure your account immediately: http://{domain}/{path}",
        "Your {service} cloud storage is full and emails are bouncing. Upgrade 50GB storage for free today: http://{domain}/{path}",
        "Action Required: We detected multiple failed login attempts on your {service} account. Verify your identity at http://{domain}/{path}",
        "Your {service} subscription could not be renewed due to billing failure. Update payment information: http://{domain}/{path}",
        "{service} Team: You have 1 unread encrypted voice message waiting. Listen now at http://{domain}/{path}",
        "Congratulations! Your {service} profile has been approved for the Verified Badge. Claim your badge at http://{domain}/{path}"
    ]
    services = ['Google', 'Microsoft Office 365', 'Apple ID', 'Netflix', 'Amazon Prime', 'Facebook', 'Instagram', 'PayPal', 'LinkedIn']

    # Category 3: Package Delivery & Courier Smishing
    delivery_phishing_templates = [
        "Your package from {courier} with tracking #US9482019 could not be delivered due to incomplete address. Update address: http://{domain}/{path}",
        "{courier} Alert: Outstanding customs fee of $2.49 is required for delivery of your parcel. Pay fee here: http://{domain}/{path}",
        "We attempted delivery of your {courier} parcel today at 11:30 AM. Reschedule delivery now: http://{domain}/{path}",
        "{courier} Shipping update: Your parcel is held at our local distribution center. Confirm delivery slot: http://{domain}/{path}",
        "Notification from {courier}: Package delivery failed. Click the link to update your shipping preference: http://{domain}/{path}"
    ]
    couriers = ['USPS', 'FedEx', 'DHL Express', 'UPS', 'Amazon Logistics', 'Royal Mail', 'India Post']

    # Category 4: Crypto & Investment Scams
    crypto_phishing_templates = [
        "Binance Security: Your cryptocurrency wallet is pending suspension due to regulatory update. Verify KYC: http://{domain}/{path}",
        "MetaMask Alert: Your seed phrase must be synchronized with the new network upgrade. Connect wallet: http://{domain}/{path}",
        "Congratulations! You were selected for the Ethereum 5.0 ETH Airdrop. Claim your free tokens here: http://{domain}/{path}",
        "Coinbase Notification: Unauthorized withdrawal of 0.85 BTC initiated. Click to cancel immediately: http://{domain}/{path}",
        "TrustWallet Notice: Security update required for all multi-coin wallets. Update wallet keys: http://{domain}/{path}"
    ]

    # Category 5: Prize, Lottery, Gift Card & Job Scams
    prize_job_phishing_templates = [
        "Congratulations! You won a $1,000 Walmart Gift Card in our annual customer sweepstakes! Claim here: http://{domain}/{path}",
        "You have been selected for a remote Data Entry position ($45/hr). Review job description and apply: http://{domain}/{path}",
        "Exclusive Amazon Shopper Reward! Complete a 30-second survey to claim your iPhone 15 Pro: http://{domain}/{path}",
        "URGENT: Your $500 Target Voucher expires in 2 hours! Click to redeem before midnight: http://{domain}/{path}",
        "IRS Notice: You have an unclaimed federal tax refund of $1,420.50. Submit your bank account details: http://{domain}/{path}"
    ]

    # Category 6: Raw Malicious URLs / Shortener Attacks
    raw_url_phishing_templates = [
        "http://{domain}/{path}?token={rand_token}&redirect=login",
        "https://{shortener}/{rand_slug}",
        "http://{domain}/{path}#user_email=target@victim.com",
        "http://admin:admin@{domain}:{port}/{path}",
        "http://{domain}/download/invoice_{rand_id}.pdf.exe"
    ]

    # Category 7: Multi-lingual Phishing
    multilingual_phishing_templates = [
        "Achtung: Ihr Bankkonto wurde vorubergehend gesperrt. Bitte verifizieren Sie Ihre Daten: http://{domain}/{path}",
        "Attention: Votre compte PayPal a ete restreint. Mettez a jour vos informations: http://{domain}/{path}",
        "Aviso importante: Su cuenta bancaria requiere verificacion de seguridad inmediata: http://{domain}/{path}",
        "Konto Gesperrt: Sicherheitswarnung zu Ihrem Sparkasse Online-Banking. Jetzt freischalten: http://{domain}/{path}"
    ]

    # Generate Phishing Samples (~2,100 samples)
    for _ in range(350):
        t = np.random.choice(bank_phishing_templates).format(
            bank=np.random.choice(banks),
            domain=np.random.choice(phishing_domains),
            path=np.random.choice(phishing_paths)
        )
        phishing_samples.append(t)

    for _ in range(400):
        t = np.random.choice(tech_phishing_templates).format(
            service=np.random.choice(services),
            domain=np.random.choice(phishing_domains),
            path=np.random.choice(phishing_paths)
        )
        phishing_samples.append(t)

    for _ in range(350):
        t = np.random.choice(delivery_phishing_templates).format(
            courier=np.random.choice(couriers),
            domain=np.random.choice(phishing_domains),
            path=np.random.choice(phishing_paths)
        )
        phishing_samples.append(t)

    for _ in range(250):
        t = np.random.choice(crypto_phishing_templates).format(
            domain=np.random.choice(phishing_domains),
            path=np.random.choice(phishing_paths)
        )
        phishing_samples.append(t)

    for _ in range(300):
        t = np.random.choice(prize_job_phishing_templates).format(
            domain=np.random.choice(phishing_domains),
            path=np.random.choice(phishing_paths)
        )
        phishing_samples.append(t)

    for _ in range(350):
        t = np.random.choice(raw_url_phishing_templates).format(
            domain=np.random.choice(phishing_domains),
            shortener=np.random.choice(shorteners),
            path=np.random.choice(phishing_paths),
            rand_token=f"{np.random.randint(100000, 999999)}",
            rand_slug=f"claim-{np.random.randint(100, 999)}",
            rand_id=f"{np.random.randint(1000, 9999)}",
            port=np.random.choice([8080, 8000, 8443, 8888])
        )
        phishing_samples.append(t)

    for _ in range(150):
        t = np.random.choice(multilingual_phishing_templates).format(
            domain=np.random.choice(phishing_domains),
            path=np.random.choice(phishing_paths)
        )
        phishing_samples.append(t)

    # =========================================================================
    # 2. LEGITIMATE TEMPLATES & HARD NEGATIVES
    # =========================================================================
    legit_domains = [
        'google.com', 'amazon.com', 'github.com', 'wikipedia.org', 'nytimes.com',
        'microsoft.com', 'apple.com', 'zoom.us', 'linkedin.com', 'slack.com',
        'dropbox.com', 'notion.so', 'stackoverflow.com', 'medium.com', 'bbc.com',
        'cnn.com', 'reuters.com', 'chase.com', 'bankofamerica.com', 'wellsfargo.com',
        'paypal.com', 'netflix.com', 'spotify.com', 'uber.com', 'airbnb.com',
        'reddit.com', 'mozilla.org', 'python.org', 'docker.com', 'cloudflare.com',
        'stripe.com', 'gov.uk', 'usa.gov', 'nih.gov', 'harvard.edu', 'mit.edu'
    ]

    legit_paths = [
        'search', 'docs/api', 'products/security', 'article/technology', 'en-US/docs/Web',
        'torvalds/linux', 'wiki/Cybersecurity', 'questions/12345678', 'dashboard/analytics',
        'account/settings', 'track/order-status', 'releases/tag/v2.4.0', 'pricing', 'support/faq'
    ]

    # Category 1: Hard Negatives — Real 2FA / OTP & Verification Messages
    hard_negative_otp_templates = [
        "Your {bank} OTP for online transaction of ${amount} is {otp}. Valid for 10 minutes. Do not share this OTP with anyone.",
        "Your Google verification code is {otp}. Don't share it with anyone.",
        "Use verification code {otp} for {service} authentication. This code will expire in 5 minutes.",
        "{service} Security Code: {otp}. If you did not request this, please change your password at https://{domain}/security",
        "Your one-time passcode for {bank} NetBanking login is {otp}. Never disclose your password or OTP to bank officials.",
        "Your Uber verification code is {otp}. Never share this code with anyone, including drivers.",
        "Microsoft account password reset code: {otp}. Enter this on the password reset page."
    ]

    # Category 2: Hard Negatives — Real Order & Delivery Updates (with "verify", "order #", "track")
    hard_negative_delivery_templates = [
        "Your Amazon order #{order_id} has shipped and will arrive on {day}. Track package at https://www.amazon.com/progress-tracker/{order_id}",
        "FedEx Tracking: Your shipment #{order_id} is out for delivery today by 8:00 PM. No signature required.",
        "USPS: Package #{order_id} was delivered in/at the mailbox at 2:15 PM on {day}.",
        "Your order #{order_id} with {company} has been confirmed. View receipt and estimated delivery date at https://{domain}/orders/{order_id}",
        "DHL Express: Shipment #{order_id} has cleared customs and is scheduled for delivery on {day}."
    ]

    # Category 3: Hard Negatives — Real Corporate & Urgent Work Communications
    hard_negative_work_templates = [
        "URGENT: All hands incident response bridge is live regarding production database latency: https://meet.google.com/{meet_id}",
        "Reminder: Please verify and submit your quarterly expense reports before Friday EOD via https://{domain}/expenses",
        "Hi team, please review the security audit checklist before our deployment at 4 PM: https://{domain}/docs/{path}",
        "Weekly engineering standup meeting is starting now: https://zoom.us/j/{zoom_id}",
        "Here is the pull request for the authentication bug fix. Please review: https://github.com/org/repo/pull/{pr_id}",
        "Your monthly cloud infrastructure report for Q3 is ready to download: https://{domain}/reports/q3-infra.pdf",
        "Please update your emergency contact information in the HR portal: https://{domain}/hr/profile"
    ]

    # Category 4: Hard Negatives — Real Billing Receipts & Invoices
    hard_negative_billing_templates = [
        "Thank you for your payment! Your monthly {service} subscription receipt for ${amount} is ready at https://{domain}/receipts/{order_id}",
        "Your electricity bill of ${amount} for account #{order_id} was paid successfully on {day}. Thank you.",
        "GitHub billing receipt: Your subscription for Copilot has renewed for ${amount}. Invoice #{order_id} available in billing settings.",
        "Apple Store Receipt: Your purchase of {service} ($4.99) has been processed. Order ID: #{order_id}."
    ]

    # Category 5: Standard Web URLs & Documentation
    legit_url_templates = [
        "https://{domain}/{path}",
        "https://www.{domain}/{path}?query=tutorial&lang=en",
        "https://{domain}/wiki/{path}",
        "https://{domain}/docs/{path}#overview",
        "https://{domain}/blog/2026/cybersecurity-architecture-overview"
    ]

    # Category 6: Standard Conversational & Newsletter Messages
    legit_conversation_templates = [
        "Hey, check out this great article on distributed systems: https://{domain}/{path}",
        "Thanks for signing up for our weekly developer newsletter! You can manage your preferences at https://{domain}/preferences",
        "Hi Alex, let's catch up over coffee tomorrow around 10 AM. Let me know if that works.",
        "You have successfully unsubscribed from marketing promotional emails.",
        "Here are the meeting minutes from yesterday's sync with the product team: https://docs.google.com/document/d/{doc_id}",
        "Great job on the presentation today! Slides are uploaded here: https://{domain}/slides/2026"
    ]

    days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
    companies = ['Apple', 'Target', 'Best Buy', 'Walmart', 'Nike', 'Zara']

    # Generate Legitimate Samples (~2,100 samples)
    for _ in range(400):
        t = np.random.choice(hard_negative_otp_templates).format(
            bank=np.random.choice(banks),
            service=np.random.choice(services),
            amount=f"{np.random.randint(15, 800)}.00",
            otp=f"{np.random.randint(100000, 999999)}",
            domain=np.random.choice(legit_domains)
        )
        legitimate_samples.append(t)

    for _ in range(350):
        t = np.random.choice(hard_negative_delivery_templates).format(
            order_id=f"{np.random.randint(100, 999)}-{np.random.randint(1000000, 9999999)}",
            day=np.random.choice(days),
            company=np.random.choice(companies),
            domain=np.random.choice(legit_domains)
        )
        legitimate_samples.append(t)

    for _ in range(400):
        t = np.random.choice(hard_negative_work_templates).format(
            domain=np.random.choice(legit_domains),
            meet_id=f"abc-{np.random.randint(1000, 9999)}-xyz",
            zoom_id=f"{np.random.randint(100000000, 999999999)}",
            pr_id=f"{np.random.randint(100, 5000)}",
            path=np.random.choice(legit_paths)
        )
        legitimate_samples.append(t)

    for _ in range(300):
        t = np.random.choice(hard_negative_billing_templates).format(
            service=np.random.choice(['Spotify Premium', 'Netflix Standard', 'Google One 2TB', 'YouTube Premium', 'AWS Cloud Services']),
            amount=f"{np.random.randint(5, 120)}.{np.random.choice(['99', '00', '50'])}",
            order_id=f"INV-{np.random.randint(100000, 999999)}",
            day=np.random.choice(days),
            domain=np.random.choice(legit_domains)
        )
        legitimate_samples.append(t)

    for _ in range(400):
        t = np.random.choice(legit_url_templates).format(
            domain=np.random.choice(legit_domains),
            path=np.random.choice(legit_paths)
        )
        legitimate_samples.append(t)

    for _ in range(300):
        t = np.random.choice(legit_conversation_templates).format(
            domain=np.random.choice(legit_domains),
            path=np.random.choice(legit_paths),
            doc_id=f"1x{np.random.randint(10000, 99999)}kL{np.random.randint(100, 999)}"
        )
        legitimate_samples.append(t)

    # Combine & Deduplicate
    phishing_df = pd.DataFrame({'text': phishing_samples, 'label': 1}).drop_duplicates(subset=['text'])
    legit_df = pd.DataFrame({'text': legitimate_samples, 'label': 0}).drop_duplicates(subset=['text'])

    # Balance datasets to equal sizes (2000 per class = 4000 total)
    n_samples = min(len(phishing_df), len(legit_df), 2000)
    phishing_df = phishing_df.sample(n=n_samples, random_state=42)
    legit_df = legit_df.sample(n=n_samples, random_state=42)

    df = pd.concat([phishing_df, legit_df], ignore_index=True).sample(frac=1.0, random_state=42).reset_index(drop=True)

    os.makedirs('data', exist_ok=True)
    df.to_csv('data/phishing_dataset.csv', index=False)
    print(f"Generated clean, deduplicated dataset at data/phishing_dataset.csv with {len(df)} total samples ({n_samples} Phishing, {n_samples} Legitimate).")
    return df

def build_model_pipeline():
    """
    Builds a multi-view feature pipeline combining Word-level and Character-level n-grams
    with a tuned, balanced Logistic Regression classifier.
    """
    feature_union = FeatureUnion([
        ('word_tfidf', TfidfVectorizer(
            analyzer='word',
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True
        )),
        ('char_tfidf', TfidfVectorizer(
            analyzer='char_wb',
            ngram_range=(3, 5),
            max_features=12000,
            sublinear_tf=True
        ))
    ])

    pipeline = Pipeline([
        ('features', feature_union),
        ('clf', LogisticRegression(
            C=3.0,
            solver='lbfgs',
            max_iter=1000,
            class_weight='balanced',
            random_state=42
        ))
    ])
    return pipeline

def train():
    df = create_dataset()

    X = df['text']
    y = df['label']

    print("\n" + "=" * 60)
    print("      5-FOLD STRATIFIED CROSS-VALIDATION")
    print("=" * 60)

    pipeline = build_model_pipeline()
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    scoring = ['accuracy', 'precision', 'recall', 'f1', 'roc_auc']
    cv_results = cross_validate(pipeline, X, y, cv=cv, scoring=scoring, return_train_score=False)

    print(f"5-Fold CV Accuracy:  {cv_results['test_accuracy'].mean() * 100:.2f}% (+/- {cv_results['test_accuracy'].std() * 100:.2f}%)")
    print(f"5-Fold CV Precision: {cv_results['test_precision'].mean() * 100:.2f}% (+/- {cv_results['test_precision'].std() * 100:.2f}%)")
    print(f"5-Fold CV Recall:    {cv_results['test_recall'].mean() * 100:.2f}% (+/- {cv_results['test_recall'].std() * 100:.2f}%)")
    print(f"5-Fold CV F1-Score:  {cv_results['test_f1'].mean() * 100:.2f}% (+/- {cv_results['test_f1'].std() * 100:.2f}%)")
    print(f"5-Fold CV ROC-AUC:   {cv_results['test_roc_auc'].mean():.4f} (+/- {cv_results['test_roc_auc'].std():.4f})")

    print("\n" + "=" * 60)
    print("      TRAIN / HELD-OUT TEST SPLIT (80/20)")
    print("=" * 60)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    test_df = pd.DataFrame({'text': X_test, 'label': y_test})
    test_df.to_csv('data/test_set.csv', index=False)
    print(f"Saved {len(test_df)} held-out test samples to data/test_set.csv")

    print("\nFitting full model pipeline on training set...")
    pipeline.fit(X_train, y_train)

    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]

    print("\nClassification Report (Held-Out Test Set):")
    print(classification_report(y_test, y_pred, target_names=["Legitimate (0)", "Phishing (1)"]))

    os.makedirs('models', exist_ok=True)
    model_path = 'models/phishing_model.pkl'
    joblib.dump(pipeline, model_path)
    print(f"Trained model pipeline successfully saved to {model_path}")

if __name__ == "__main__":
    train()
