import os
import joblib
import pandas as pd
import numpy as np
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
    classification_report
)

MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models', 'phishing_model.pkl')
TEST_DATASET_PATH = os.path.join(os.path.dirname(__file__), 'data', 'test_set.csv')

def benchmark():
    print("=" * 70)
    print("        CYBER SHIELD - ADVANCED ML BENCHMARK & EVALUATION")
    print("=" * 70)

    if not os.path.exists(MODEL_PATH):
        print(f"Error: Model not found at {MODEL_PATH}. Please run train_model.py first.")
        return

    model = joblib.load(MODEL_PATH)
    print(f"Loaded pipeline model from: {MODEL_PATH}")

    # 1. Benchmark on Held-Out Test Set (80/20 split from 3,684 samples)
    if os.path.exists(TEST_DATASET_PATH):
        df_heldout = pd.read_csv(TEST_DATASET_PATH)
        X_h = df_heldout['text']
        y_h_true = df_heldout['label']
        y_h_pred = model.predict(X_h)
        y_h_proba = model.predict_proba(X_h)[:, 1] if hasattr(model, "predict_proba") else y_h_pred

        acc_h = accuracy_score(y_h_true, y_h_pred)
        prec_h = precision_score(y_h_true, y_h_pred)
        rec_h = recall_score(y_h_true, y_h_pred)
        f1_h = f1_score(y_h_true, y_h_pred)
        roc_h = roc_auc_score(y_h_true, y_h_proba)
        cm_h = confusion_matrix(y_h_true, y_h_pred)

        print("\n[1] Held-Out Test Split (20% Stratified Split from 3,684 Samples):")
        print(f"    - Total Test Samples: {len(df_heldout)}")
        print(f"    - Accuracy:           {acc_h * 100:.2f}%")
        print(f"    - Precision:          {prec_h * 100:.2f}%")
        print(f"    - Recall:             {rec_h * 100:.2f}%")
        print(f"    - F1-Score:           {f1_h * 100:.2f}%")
        print(f"    - ROC-AUC:            {roc_h:.4f}")
        print(f"\n    Confusion Matrix:")
        print(f"    [[TN: {cm_h[0][0]:3d}  FP: {cm_h[0][1]:3d}]")
        print(f"     [FN: {cm_h[1][0]:3d}  TP: {cm_h[1][1]:3d}]]")

    # 2. Out-of-Sample Hand-Curated Real-World Validation Set (50 samples)
    real_world_samples = [
        # Phishing samples (Label: 1) - 25 samples
        ("http://paypal-security-center-update.com/login.php", 1),
        ("http://192.168.0.100/secure-banking/verify", 1),
        ("Urgent notice: Your Netflix membership is on hold. Update billing now at http://netflix-billing-update.xyz", 1),
        ("Claim your $500 Walmart voucher before midnight! Visit: http://bit.ly/walmart-voucher-claim", 1),
        ("Wells Fargo Alert: Suspicious transaction detected. Confirm OTP at http://wellsfargo-verify.club", 1),
        ("http://appleid.apple.com.verify-login.tk/auth", 1),
        ("Your package delivery has failed. Update address: http://dhl-express-tracking.top/track", 1),
        ("Microsoft Office 365: Password expires today. Keep same password at http://office365-login-verify.click", 1),
        ("Unusual login attempt from Russia. Secure your account: http://facebook-security-alert.net", 1),
        ("We tried to deliver your parcel today. Reschedule at http://usps-post-delivery.com", 1),
        ("Your Amazon account is locked. Verify identity at http://amazon-verify-account.tk", 1),
        ("Notice of Tax Return. View document at http://irs-gov-refund.net", 1),
        ("Important: Your iCloud storage is full. Upgrade now for free: http://apple-icloud-upgrade.xyz", 1),
        ("Zoom Meeting Invitation. Click here to join: http://zoom-meeting-invite.tk", 1),
        ("You have an encrypted message from HR. Open at http://company-hr-portal.com/login", 1),
        ("Verify your cryptocurrency wallet to prevent suspension: http://coinbase-secure-verify.net", 1),
        ("Congratulations! You won the European EuroMillions lottery! Claim at http://euromillions-winner.top", 1),
        ("MetaMask Notification: Restore your 12-word seed phrase: http://metamask-sync-wallet.click", 1),
        ("HDFC Bank Alert: Your NetBanking account will be blocked today due to pending KYC. Update at http://hdfc-kyc-verify.online", 1),
        ("Your Uber ride receipt is ready. If you did not take this ride, dispute at http://uber-receipt-dispute.xyz", 1),
        ("Adobe Creative Cloud: Payment declined. Update credit card at http://adobe-account-billing.club", 1),
        ("Achtung: Ihr Sparkasse Online-Konto ist gesperrt: http://sparkasse-sicherheit.xyz/login", 1),
        ("Immediate action required: Dropbox storage quota exceeded. Upgrade at http://dropbox-quota-upgrade.site", 1),
        ("http://admin:admin@192.168.1.1:8080/router-login", 1),
        ("Work from home job offer: $450/day. Submit your CV and SSN at http://remote-hiring-now.work", 1),

        # Legitimate samples & Hard Negatives (Label: 0) - 25 samples
        ("https://www.google.com/search?q=cybersecurity+best+practices", 0),
        ("https://github.com/torvalds/linux/commits/master", 0),
        ("https://en.wikipedia.org/wiki/Phishing", 0),
        ("https://aws.amazon.com/products/security/", 0),
        ("https://developer.mozilla.org/en-US/docs/Web/HTTP", 0),
        ("Hey team, here is the document for tomorrow's standup meeting: https://docs.google.com/document/d/123", 0),
        ("Your Amazon order has shipped and will arrive Thursday. Track in your Amazon app.", 0),
        ("Hi John, let's connect on Zoom at 3pm: https://zoom.us/j/123456789", 0),
        ("Bank of America: Your one-time passcode is 492013. Do not share this code.", 0),
        ("FedEx: Your package is out for delivery. View tracking updates here.", 0),
        ("URGENT: Server outage reported. Please join the incident response bridge immediately.", 0),
        ("You have successfully unsubscribed from our newsletter.", 0),
        ("Your IRS tax return has been accepted.", 0),
        ("Please verify your email address to complete registration on LinkedIn.", 0),
        ("Your Dropbox file has finished syncing.", 0),
        ("Slack: You have 3 new notifications in the #general channel.", 0),
        ("Your OTP for SBI Net Banking transaction is 482910. Do not share this OTP with anyone. - SBI", 0),
        ("Your monthly Spotify Premium subscription receipt of $10.99 is available in your account settings.", 0),
        ("Google Security Alert: Your password was recently changed. If this was you, no action is needed.", 0),
        ("GitHub: New security vulnerability alert in repository expressjs/express. Run npm audit fix.", 0),
        ("Apple Store: Your order #W982340192 has been confirmed. Delivery expected Monday.", 0),
        ("Could you please review my pull request for the auth bug fix at https://github.com/myorg/api/pull/402?", 0),
        ("Reminder: Team quarterly planning workshop tomorrow from 9:00 AM to 1:00 PM in Conference Room B.", 0),
        ("Your Uber ride with driver Michael has ended. Total fare: $18.45. Receipt sent to your email.", 0),
        ("https://stackoverflow.com/questions/248946/how-to-fix-ssl-certificate-verify-failed-in-python", 0)
    ]

    df_test = pd.DataFrame(real_world_samples, columns=['text', 'label'])
    y_test_true = df_test['label']
    y_test_pred = model.predict(df_test['text'])
    y_test_proba = model.predict_proba(df_test['text'])[:, 1]

    rw_acc = accuracy_score(y_test_true, y_test_pred)
    rw_prec = precision_score(y_test_true, y_test_pred)
    rw_rec = recall_score(y_test_true, y_test_pred)
    rw_f1 = f1_score(y_test_true, y_test_pred)
    rw_roc = roc_auc_score(y_test_true, y_test_proba)
    cm_rw = confusion_matrix(y_test_true, y_test_pred)

    print("\n[2] Separate Real-World Validation Set (50 Hand-Curated Samples, Out-of-Sample):")
    print(f"    - Total Samples:      {len(df_test)} (25 Phishing, 25 Legitimate)")
    print(f"    - Real-World Acc:     {rw_acc * 100:.2f}%")
    print(f"    - Real-World Prec:    {rw_prec * 100:.2f}%")
    print(f"    - Real-World Rec:     {rw_rec * 100:.2f}%")
    print(f"    - Real-World F1:      {rw_f1 * 100:.2f}%")
    print(f"    - Real-World ROC-AUC: {rw_roc:.4f}")
    print(f"\n    Confusion Matrix:")
    print(f"    [[TN: {cm_rw[0][0]:2d}  FP: {cm_rw[0][1]:2d}]")
    print(f"     [FN: {cm_rw[1][0]:2d}  TP: {cm_rw[1][1]:2d}]]")

    print("\n" + "=" * 70)
    print("Detailed Classification Report (Real-World Out-of-Sample):")
    print(classification_report(y_test_true, y_test_pred, target_names=["Legitimate (0)", "Phishing (1)"]))
    print("=" * 70)

    # 3. Automated Error Analysis
    errors = []
    for idx, (text, true_lbl, pred_lbl, prob) in enumerate(zip(df_test['text'], y_test_true, y_test_pred, y_test_proba)):
        if true_lbl != pred_lbl:
            err_type = "False Positive (Legit classified as Phishing)" if pred_lbl == 1 else "False Negative (Phishing classified as Legit)"
            errors.append({
                "index": idx + 1,
                "text": text,
                "true_label": "Legitimate (0)" if true_lbl == 0 else "Phishing (1)",
                "predicted_label": "Phishing (1)" if pred_lbl == 1 else "Legitimate (0)",
                "phishing_prob": f"{prob * 100:.1f}%",
                "type": err_type
            })

    print(f"\n[3] Error Analysis ({len(errors)} misclassifications out of {len(df_test)} samples):")
    if not errors:
        print("    No errors found on this validation set! All samples classified correctly.")
    else:
        for i, err in enumerate(errors, 1):
            print(f"\n    Error #{i}: {err['type']}")
            print(f"    Sample:         \"{err['text']}\"")
            print(f"    True Label:     {err['true_label']}")
            print(f"    Predicted:      {err['predicted_label']} (Phishing Probability: {err['phishing_prob']})")
            # Explanations
            if "verify-failed" in err['text']:
                print(f"    Reason/Insight: Contains 'verify-failed' in URL path mimicking phishing tokens.")
            elif "URGENT:" in err['text']:
                print(f"    Reason/Insight: Urgent server outage message contains high-urgency keywords without full domain context.")
            else:
                print(f"    Reason/Insight: Ambiguous lexical tokens overlapping with attack vocabulary.")
    print("=" * 70)

if __name__ == "__main__":
    benchmark()
