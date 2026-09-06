"""Revise the supplied 19-page PDF without replacing its design or artwork."""
from pathlib import Path
import json, re, sys, hashlib
import fitz

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
SOURCE=Path(sys.argv[1]) if len(sys.argv)>1 else HERE/'input/Simpaisa_Network_Playbook_2026_V2_4.pdf'
DEST=Path(sys.argv[2]) if len(sys.argv)>2 else HERE/'build/Simpaisa_Network_Playbook_2026_Final.pdf'
DEST.parent.mkdir(parents=True,exist_ok=True)
doc=fitz.open(SOURCE)
assert len(doc)==19
FONTS={'IR':fitz.Font(fontfile=str(HERE/'fonts/Inter.ttf')),'IB':fitz.Font(fontfile=str(HERE/'fonts/InterSemi.ttf')),'PH':fitz.Font(fontfile=str(HERE/'fonts/Poppins.ttf'))}
NAVY=(0.0,0.094,0.40); BLUE=(0.004,0.337,0.984); BODY=(0.20,0.27,0.39); MUTED=(0.32,0.39,0.50); WHITE=(1,1,1)
ops=[[] for _ in doc]; logs=[]; originals=[]
for page in doc:
 originals.append(page.get_text('dict'))
 for name,path in [('IR','Inter.ttf'),('IB','InterSemi.ttf'),('PH','Poppins.ttf')]:page.insert_font(fontname=name,fontfile=str(HERE/'fonts'/path))

def norm(t):return re.sub(r'\s+',' ',t).strip()
def clean(t):
 return t.replace('\u2014','; ').replace('\u2013','-').replace('\u2011','-').replace('\u00a0',' ').replace('’',"'").replace('‘',"'")
def region(n,rect,text,size=9.2,font='IR',color=BODY,leading=None,align='left',clear=None,fill=None):
 rect=fitz.Rect(rect);c=fitz.Rect(clear) if clear is not None else rect
 ops[n-1].append({'rect':list(rect),'clear':list(c),'text':clean(text),'size':size,'font':font,'color':color,'leading':leading or size*1.28,'align':align,'fill':fill})
def blocks(n):
 return [b for b in originals[n-1]['blocks'] if 'lines' in b]
def spans(n):return [s for b in blocks(n) for l in b['lines'] for s in l['spans']]
def block(n,needle,text,size=None,font=None,color=None,w=None):
 matches=[b for b in blocks(n) if needle in norm(' '.join(s['text'] for l in b['lines'] for s in l['spans']))]
 assert len(matches)==1,(n,needle,len(matches))
 b=matches[0];s=b['lines'][0]['spans'][0];r=fitz.Rect(b['bbox']);f=font or ('PH' if 'Poppins' in s['font'] else 'IB' if 'Semi' in s['font'] or 'Bold' in s['font'] else 'IR')
 if w:r.x1=r.x0+w
 col=color or tuple(((s['color']>>shift)&255)/255 for shift in (16,8,0))
 region(n,r,text,size or s['size'],f,col,clear=b['bbox'])
def exact(n,old,new,size=None,font=None,color=None,width=None):
 matches=[s for s in spans(n) if norm(s['text'])==old]
 assert len(matches)==1,(n,old,len(matches))
 s=matches[0];r=fitz.Rect(s['bbox']);r.x1=r.x0+(width or r.width+1)
 f=font or ('PH' if 'Poppins' in s['font'] else 'IB' if 'Semi' in s['font'] or 'Bold' in s['font'] else 'IR')
 col=color or tuple(((s['color']>>shift)&255)/255 for shift in (16,8,0))
 region(n,r,new,size or s['size'],f,col,clear=s['bbox'])

# Headings and short introductions retain all original panels and their positions.
block(4,'Overview','Simpaisa and our network',w=515)
block(5,'Our Relevant Use Cases','How businesses use Simpaisa',w=515)
block(6,'Built for Scale. Engineered for Trust.','How payments move through Simpaisa',w=515)
block(7,'Simpaisa network outreach','Wallet growth in Pakistan and Bangladesh',w=515)
block(7,'The growing wallet base','National account bases | 2023 to 2025',w=515)
block(7,'Our payment primitives','Wallets, A2A and domestic schemes by market',w=515)
block(8,'Market readiness at a glance','Payment landscape and Simpaisa coverage',w=515)
block(17,'Remittance corridors','Remittance receive markets',w=515)
region(2,(40,76,555,109),'Simpaisa connects businesses to wallets, bank transfers and cards across seven markets. One integration supports acceptance, disbursements and remittance payout.',10,leading=14)
for y,h,t in [(205,32,'Founded in 2016 and headquartered in Singapore. PCI DSS Level 1 and ISO 27001 certified; 100+ merchants across more than ten use cases.'),(253,32,'Pakistan, Bangladesh, Nepal, Iraq, Egypt, Saudi Arabia and Nigeria. Together, these markets have a population of about 880m.'),(301,43,'Wallets, bank transfers and cards. Acceptance in seven markets, disbursements in four and remittance payout in five.'),(363,43,'Across supported payment methods, Simpaisa processes 275m+ transactions and USD 1bn+ annually. It serves 30m+ unique merchant end users.'),(425,43,'When local wallets or bank transfers are missing at checkout, businesses risk losing the sale and the customer.')]:
 region(2,(166,y,539,y+h),t,9.6,leading=13)
block(2,'Recognised by the industry','Industry recognition',w=490)
block(2,'Five industry awards','Five awards for growth, B2B payments, platform services and payment facilitation in 2025 and 2026.',w=491)
region(4,(40,74,555,130),'Founded in 2016 and headquartered in Singapore, Simpaisa connects digital businesses to local payment methods. We support gaming, streaming, marketplaces and mobility businesses across the Middle East, South Asia and Africa.',10,leading=14)
region(4,(40,142,555,199),'Our network supports merchant acceptance (C2B), disbursements (B2C) and remittance (C2C). One API connects a business to the available methods in each market. Licensed partners handle funds; Simpaisa provides payment processing, routing and reconciliation.',10,leading=14)
block(4,'Merchants collect payments through','Collect through local wallets, bank transfers, cards and supported cash-payment points. Methods are enabled by market through one integration, with routing and failover.',size=9.6,w=230)
block(4,'Real-time disbursements to wallets','Send disbursements and remittance payouts to supported wallets and bank accounts. Payouts are prefunded through licensed partners. Destination, timing and settlement terms depend on the market and method.',size=9.6,w=229)
block(4,'Payment infrastructure for the region','Collections and payouts for digital businesses',w=491)
block(4,'Global aggregators, gaming publishers','Combined processing across supported payment methods, serving merchant end users across payments, gaming, commerce and mobility.',size=9.2,w=491)
# Use the same definitions wherever the operating figures repeat.
region(2,(307,523.4,419,533),'transactions processed annually',6.8,color=MUTED,align='center',clear=(330,522,395,534))
region(2,(437,523.4,550,533),'annual payment value processed',6.8,color=MUTED,align='center',clear=(462,522,525,534))
for x,t in [(58,'transactions processed annually'),(224,'annual payment value processed'),(391,'unique merchant end users served')]:
 region(4,(x,744.6,x+146,755),t,7,color=WHITE,align='center',clear=(x,744,x+146,754))
region(5,(40,73,555,104),'Customers pay through wallets, bank accounts and cards. Simpaisa connects businesses to those methods for purchases, disbursements and remittance payout.',9.8,leading=13.5)
region(5,(140,112,550,130),'Payment options for everyday purchases',9.4,clear=(139,112,555,129))
for x,t in [(52,'Top-ups and in-game purchases, with payment confirmation.'),(182.75,'Digital payment at marketplace checkout, including prepaid orders.'),(313.5,'Subscriptions with supported recurring methods, retries and opt-out.'),(444.25,'Fare collection and driver payouts, reconciled in one file.')]:
 region(5,(x,180,x+99,224),t,9.1,leading=11.8)
for x,t in [(52,'Reseller settlements and refunds through supported local wallets and bank accounts.'),(226.33,'Screened withdrawals and prize payouts to player wallets and bank accounts.'),(400.66,'Payouts to freelancers, contractors and gig workers, with reconciliation.')]:
 region(5,(x,352,x+143,386),t,9.2,leading=11.7)
block(5,'Wallet, bank and cash-out payouts','Remittance payout to wallets, banks and cash points, with agreed funding and FX.',size=9.2,w=230)
block(5,'Local distribution of cross-border funds','Local payout for aggregators through one connection to domestic methods.',size=9.2,w=230)
block(5,'100+ merchants across more than','Businesses served across payments, gaming, commerce and mobility.',w=491)
region(6,(40,73,555,102),'Simpaisa processes payment instructions, routes transactions and provides reconciliation. Licensed partners hold settlement funds and make local payouts.',9.8,leading=13.5)
region(6,(40,140,555,179),'Payments are collected in local currency. Licensed partners hold funds and settle merchants in the agreed currency. Simpaisa provides processing, routing, reconciliation and FX instructions without taking possession or control of settlement funds.',9.6,leading=13)
region(6,(263,393,333,424),'Prefunded\npayout balances',8.5,'IB',NAVY,leading=12,align='center',clear=(272,389,326,426))
exact(6,'AI-assisted incident monitoring','Incident detection and alerts',width=205)
region(6,(200,696,544,710),'PCI DSS Level 1 (v4.0.1) | ISO/IEC 27001:2022',8.5,color=WHITE)

# Exact reporting periods, rather than new totals, on the existing page 7 table.
periods=[('SBP | Jun 2025','SBP | Jan-Mar 2026','1LINK | reported 2026'),('BB | Dec 2025','BB | 2025','BB | 2025'),('NRB | Jul 2025','NRB | Jul 2025','NCHL | Dec 2025'),('CBI | Apr-Jun 2025','CBI | Sep 2025','CBI | 2025'),('CBE | Jun 2025','CBE | to Jun 2025','CBE | Jun 2025'),('Al Rajhi | 2025','SAMA | 2025','SAMA | 2025'),('OPay | reported 2026','NIBSS | 2024','Operators | 2025')]
for i,row in enumerate(periods):
 for x,t in zip([144,284.33,424.66],row):region(7,(x,444.0+i*44,x+125,454+i*44),t,7.1,color=MUTED)
region(7,(424.66,551,548,575),'No domestic scheme\nRetail cards on page 12',8.2,'IB',NAVY,leading=12)
region(7,(52,752,543,778),'One integration for local payment choice, settlement through licensed partners and a shared reconciliation file.',9.2,color=WHITE,leading=12.5)
# Match the common title and footer baselines without changing page geometry.
for s in spans(7):
 if s['bbox'][1]>800:
  r=fitz.Rect(s['bbox']);region(7,(r.x0,r.y0-2,r.x1+1,r.y1-2),s['text'],s['size'],color=tuple(((s['color']>>k)&255)/255 for k in (16,8,0)),clear=r)

# Same page 8 matrix, with unranked indicators and the original blue palette.
block(8,'The seven markets compared','Selected wallet, bank-transfer and card indicators, alongside Simpaisa service coverage. Each figure retains its own definition and reporting period; the table does not rank market maturity.',size=9.6,w=515)
region(8,(40,121,345,135),'Market context and service coverage',8.3,color=MUTED,fill=(0.914,0.914,0.914))
region(8,(118,149,210,162),'WALLET BASE',7.2,'IB',WHITE)
region(8,(217,149,309,162),'BANK TRANSFERS',7.2,'IB',WHITE)
data8=[
 [('135.9m','Branchless accounts | Jun 2025'),('742.1m','Raast | Jan-Mar 2026'),('PayPak','16.1m cards in force'),('Raast / IBFT','Wallet and bank payout')],
 [('250.2m','MFS accounts | Dec 2025'),('93.9m','NPSB transfers | 2025'),('TakaPay','17 issuing banks | 2025'),('NPSB / BEFTN','MFS and bank payout')],
 [('26.8m','Wallet users | Jul 2025'),('1.44m','connectIPS users | Jul 2025'),('NEPALPAY Card','34+ principal members'),('connectIPS','Wallet and bank payout')],
 [('1.2m','Active e-wallets | 2025'),('Inter-wallet','Transfers enabled Sep 2025'),('No domestic scheme','International cards'),('Not offered','Acceptance only')],
 [('55.5m','Wallets | Jun 2025'),('16m+','InstaPay users | Jun 2025'),('Meeza','43.5m cards | Jun 2025'),('Wallets / banks','Remittance payout')],
 [('8m+ urpay','urpay customers | 2025'),('784m','sarie transfers | 2025'),('mada','1.77bn online payments | 2025'),('Not offered','Acceptance only')],
 [('45m+ OPay','Provider customers | 2026'),('11.2bn','NIP transfers | 2024'),('Verve / AfriGO','100m Verve | Africa-wide'),('NIP / wallets','Bank and wallet payout')]
]
for i,row in enumerate(data8):
 y=166+i*46
 for j,(a,b) in enumerate(row):
  x=113+j*98
  # Preserve the grid and blue colour family; remove its misleading ranking meaning.
  region(8,(x+8,y+5,x+92,y+42),a+'\n'+b,8.0,'IR',NAVY,leading=10.4,clear=(x+.3,y+.3,x+97.7,y+45.7),fill=(.925,.949,.984))
region(8,(40,494,555,514),'Wallet accounts, provider customers and transfer counts are different measures. Market totals do not represent merchant end users served by Simpaisa or its processing volume.',7.8,color=MUTED,leading=10.2)
block(8,'How to read this map','How to read this table',w=450)
block(8,'Account reach','Wallet base',w=200)
block(8,'Registered wallets or transaction accounts','National accounts or named-provider customers. Active wallets are labelled separately.',size=8.5,w=230)
block(8,'Instant rails','Bank transfers',w=200)
block(8,'Transfers a year over','Published transfer activity or user access. Each cell states the measure and period.',size=8.5,w=230)
block(8,'The national scheme and the scale','Scheme names and reported scale. Card counts, membership and payment volumes remain distinct.',size=8.5,w=230)
block(8,'Rails Simpaisa pays out on','A: acceptance. D: disbursements. R: remittance. Highlighted letters show services offered.',size=8.5,w=230)
block(8,'Wallets and instant rails carry','Local payment coverage across seven markets',w=491)
block(8,'Cards lead only in Saudi Arabia','Simpaisa supports acceptance in all seven markets, disbursements in four and remittance payout in five. The available methods differ by country.',size=9.2,w=491)
exact(8,'5 of 7','7',width=55)
exact(8,'wallet- or rail-first markets','markets with acceptance',width=108)
exact(8,'markets with wallet and rail payout','markets with remittance payout',width=131)

# Country headers retain their landmark images, titles and flags.
headers={
9:'Pakistan has 241m people and 161m broadband subscriptions. In Jan-Mar 2026, digital channels accounted for 92% of retail payments. Local wallets and Raast give customers payment options through accounts they already use.',
10:'Bangladesh has 179m people and 136m internet subscriptions. MFS providers held 250.2m registered accounts at December 2025 and processed BDT 18.7tn (about USD 152bn) during 2025. bKash and Nagad provide established wallet checkout options.',
11:'Nepal has 29m people and 31m broadband subscriptions. At July 2025, it had 26.8m wallet users and 27.7m mobile-banking users. QR payment value reached NPR 958bn (about USD 7bn) in FY2024/25, up from NPR 500bn a year earlier.',
12:'Iraq has 47m people and 84% internet penetration. Bank accounts rose from 8m in 2022 to 20m by mid-2025. Retail card payments reached IQD 8.5tn (about USD 6.5bn) in Q3 2025, alongside the development of interoperable wallet payments.',
13:'Egypt has 109m people and 94m active mobile-internet subscriptions. Mobile wallets reached 55.5m by June 2025. Wallet transaction value rose to about EGP 4tn (USD 80bn) in 2025. Meeza provides domestic card payments in Egyptian pounds.',
14:'Saudi Arabia has 35m people. In 2025, electronic payments accounted for 85% of retail payments. mada is the domestic card scheme and sarie supports instant bank transfers. Simpaisa supports mada, sarie, stc bank and urpay.',
15:'Nigeria has 242m people and 157m internet subscriptions. NIP processed 11.2bn transfers worth NGN 1,070tn (about USD 725bn) in 2024. Simpaisa connects businesses to local wallets, bank transfers and cards, with domestic settlement in naira.'}
limit_copy={
9:['Wallet debit and balance limits vary by SBP account level.','Raast: bank-set limits; minimum PKR 200,000 unless account-type limits are lower.','No daily inward-credit cap; receiving account balance and KYC limits apply.'],
10:['bKash merchant payments: no preset limit; merchant-type limits may apply.','Wallet payout limits vary by provider and route; bank-account limits apply.','bKash: BDT 250,000 per remittance, excluding incentives; other wallets vary.'],
11:['Wallet-to-bank/QR: NPR 200,000/day and NPR 1,000,000/month.','Bank-to-wallet: NPR 200,000/day, NPR 1,000,000/month; other routes vary.','Receiving wallet balance and route-specific limits apply.'],
12:['Consumer and merchant wallet tiers have different transfer and balance limits.'],
13:['InstaPay: EGP 70,000/transfer; wallet limits depend on the provider.','Receiving account and wallet balance limits apply by provider.'],
14:['sarie: up to SAR 20,000/transfer; wallet limits vary by licence and account.'],
15:['Daily wallet limits depend on the KYC tier and provider.','NIP: up to NGN 25m for individuals, subject to bank security and account limits.','Naira payout; above USD 200 equivalent must be credited to the beneficiary account.']}
for n,t in headers.items():
 region(n,(40,106,555,143),t,9.0,color=WHITE,leading=11.8)
 block(n,'Product offering','Simpaisa services',w=350)
 # Replace unclear high/medium scores with the same categories, without changing support claims.
 for s in spans(n):
  old=norm(s['text'])
  if old.startswith('High:'):
   if 'account-to-account' in old:new='Wallets, bank transfers and cards'
   elif 'OTC' in old:new='Wallets, banks and cash pickup'
   else:new='Wallets and bank accounts'
   r=fitz.Rect(s['bbox']);region(n,(r.x0,r.y0,547,r.y1+.2),new,8.6,color=BODY,clear=r)
  if old=='Available on wallets' or old=='Available on limited wallets':
   r=fitz.Rect(s['bbox']);region(n,(r.x0,r.y0,547,r.y1+.2),'Available on supported wallets',8.6,color=BODY,clear=r)
 # Preserve useful route-specific controls without claiming a universal ceiling.
 limit_index=0
 lines=[l for b in blocks(n) for l in b['lines']]
 for l in lines:
  for s in l['spans']:
   if norm(s['text'])=='Limits':
    y=s['bbox'][1];x=152 if n in [9,10,11,15] else 154
    region(n,(x,y,548,y+11),limit_copy[n][limit_index],8.6,color=BODY,clear=(x-1,y-.1,550,y+11))
    limit_index+=1
block(12,'The Central Bank of Iraq licenses','Inter-wallet transfers were introduced on 3 September 2025, including transfers to merchant wallets. This enables interoperable wallet acceptance through participating providers.',size=9.2,w=515)
# A following one-word line is part of the original Iraq paragraph.
for b in blocks(12):
 if norm(' '.join(s['text'] for l in b['lines'] for s in l['spans']))=='interoperable.':region(12,b['bbox'],'')
block(14,'Card acceptance is mature','Simpaisa adds sarie transfers and local wallets alongside a merchant\'s existing card acceptance. Supported methods and checkout journeys are agreed during onboarding.',size=9.2,w=515)
exact(15,'Multi-rail, 98.67% uptime','Multi-rail, 99% uptime',width=156)
# Keep the numeric evidence, with missing scope labels made explicit.
exact(10,'Credit-card value share (%)','Credit-card value share',width=164)
region(10,(218,200,373,211),'March 2025 | selected schemes',7.3,color=MUTED,clear=(218,200,373,211))
region(9,(218,201,373,212),'Reported shares | debit cards and usage',7.0,color=MUTED,clear=(218,201,373,212))

# Page 16: retain the comparison columns; shorten repeated prose and increase type.
block(16,'Merchant acceptance market by market','Acceptance methods and checkout journeys across the seven markets. Refunds are available; wallet tokenisation depends on the provider.',size=9.6,w=515)
checkout=[
'In-app approval; OTP where required. Raast requests accepted in the bank app.',
'Wallet redirect: number, OTP and PIN. Bangla QR approved in the app.',
'Wallet: MPIN or OTP. connectIPS: login and OTP. QR approved in the app.',
'Wallet redirect: number, PIN and SMS OTP.',
'Wallet: PIN and OTP. InstaPay: PIN or biometric. Hosted card checkout.',
'mada: hosted 3-D Secure. sarie: bank app. Wallet: OTP or in-app approval.',
'Bank transfer to a dynamic account. Wallet approval with PIN or OTP.'
]
for i,t in enumerate(checkout):
 y=144+[0,50,100,150,201,251,301][i]
 region(16,(237,y,349,y+43),t,8.3,leading=10.5)
 region(16,(359,y,450,y+43),'Real-time\nAbove 80%',8.8,leading=12)
 region(16,(461,y,549,y+43),'Refunds available'+ ('\nWallet tokenisation' if i==0 else '\nSelected wallets tokenised' if i==1 else ''),8.3,leading=10.5)
region(16,(180.59,538,244,561),'Customer\nauthorises',8.6,'IB',NAVY,leading=11)
for x,t in [(52,'Customer selects an available local method at checkout.'),(152.59,'Customer approves in the app, by redirect, QR or hosted page.'),(253.19,'Simpaisa sends payment confirmation by webhook.'),(353.8,'The licensed partner holds funds; Simpaisa routes and reconciles.'),(454.39,'Settlement follows the agreed currency and schedule.')]:
 region(16,(x,578,x+89,629),t,8.3,leading=10.7)
block(16,'Wallets, instant rails and domestic cards','Connect wallet, bank-transfer and card checkout through one API. Receive payment confirmation and reconciliation, with tokenisation where supported.',size=9.2,w=491)

# Page 17: distinguish receive-market context from confirmed sending corridors.
block(17,'Five of the seven markets','Simpaisa supports remittance payout in five receive markets. Their reported annual inflows total about USD 156bn across the periods below. These are national flows, not Simpaisa transaction volumes.',size=9.6,w=515)
region(17,(265,128,374,147),'SEND-MARKET CONTEXT',7.2,'IB',WHITE)
region(17,(383,128,472,147),'LOCAL PAYOUT',7.2,'IB',WHITE)
send=['Saudi Arabia, UAE, UK and EU. Published shares vary by period.','Saudi Arabia, UK, UAE, Malaysia and USA.','Migrant destinations: Malaysia, Qatar, Saudi Arabia and UAE.','Gulf states, USA and Europe. No source-country split shown.','USA and UK diaspora. No source-country split shown.']
rules=['PRI payout through licensed partners. Receiving-account balance and KYC limits apply.','Payout to banks or MFS wallets. Wallet limits vary by provider and remittance route.','NPR payout through licensed banks and remitters.','Wallet payout or bank credit over supported networks, including IPN.','Naira payout to the beneficiary account.']
ys=[159,229,300,351,412];ends=[219,289,339,401,442]
for i,y in enumerate(ys):
 region(17,(265,y,374,ends[i]),send[i],8.4,leading=10.8)
 region(17,(383,y,471,ends[i]),rules[i],8.4,leading=10.8)
for x,t in [(52,'USD prefund is held by the designated licensed partner.'),(152.59,'Recipient details are checked through the supported payout route.'),(253.19,'The licensed local partner credits the beneficiary.'),(353.8,'Wallet or bank payout; cash pickup is available in Pakistan.'),(454.39,'Settlement and reconciliation are reported in one format.')]:
 region(17,(x,535,x+89,580),t,8.3,leading=10.8)
region(17,(40,605,555,627),'Reporting periods differ. Send-market context does not imply every origin-to-destination route is enabled. See the linked national sources.',7.8,color=MUTED,leading=10)
block(17,'Simpaisa lands remittances','Simpaisa provides local payout for partners including TerraPay, Thunes, dLocal, MoneyGram, Ria and Tazapay, with recipient checks and shared reconciliation.',size=9.2,w=491)
exact(17,'inbound to the five markets','reported annual inflows',width=104)

exact(17,'USD 21.8bn','USD 20.9bn',width=50)
exact(17,'2025 · flat','2024 | +8.9%',width=76)
exact(17,'USD 157bn','USD 156bn',width=83)
exact(17,'FY2026 · +17.3%','FY2026 | provisional',width=77)
# Redraw the Nigeria bar proportionally on the unchanged chart scale.
region(17,(124.8,411.8,163.2,422.2),'',fill=(1,1,1))

# Page 18: keep the original steps and matrix, align its wording with actual service scope.
block(18,'A digital business adds','Add local payment acceptance across seven markets, with disbursements in four and remittance payout in five. Configure methods, test the payment journeys and agree settlement terms before launch.',size=9.6,w=515)
region(18,(281.19,157,344,180),'Configure\nmethods',8.7,'IB',NAVY,leading=11)
steptexts=['Complete KYB, MATCH and MCC checks; agree terms by market.','Connect the API and test checkout and payout journeys.','Configure methods, routing, failover and recipient checks.','Sign off limits, refunds and 3-D Secure in UAT; run a controlled pilot.','Launch approved methods; agree settlement currency and reporting.']
for x,t in zip([52,152.59,253.19,353.8,454.39],steptexts):region(18,(x,193,x+89,233),t,8.3,leading=10.4)
region(18,(40,249,555,267),'Market-specific setup',11,'PH',NAVY)
accept=['Enable selected wallets, Raast and cards. Confirm recurring-payment support.','Enable selected MFS wallets, bank transfers and cards. Test wallet authentication.','Enable wallets, connectIPS and cards. Test MPIN, OTP and QR journeys.','Enable supported wallets and cards. Test redirect, PIN and OTP.','Enable wallets, InstaPay and cards. Test authentication for each method.','Enable selected wallets, sarie and mada. Test bank-app and 3-D Secure journeys.','Enable wallets, NIP and cards. Test dynamic accounts and recipient checks.']
payout=['Disbursements and remittance: wallets or bank accounts over Raast / IBFT.','Disbursements and remittance: MFS or bank accounts over NPSB / BEFTN.','Disbursements and remittance: wallets and connectIPS bank accounts.','No disbursements or remittance. Acceptance settlement through local partners.','Remittance payout to wallets and bank accounts. No general disbursements.','No disbursements or remittance. Agree acceptance settlement with the partner.','Disbursements and remittance: bank accounts over NIP, or supported wallets.']
for i,y in enumerate([294,329,361,393,425,457,489]):
 region(18,(125,y,333,y+28),accept[i],8.3,leading=10.6)
 region(18,(344,y,548,y+28),payout[i],8.3,leading=10.6)
# Keep the original bullet anchors and restore the implementation controls.
region(18,(63,550,284,625),'',clear=(62,550,285,625))
region(18,(323.5,550,545,625),'',clear=(323,550,546,625))
for y,t in [(550.8,'One API for checkout, supported recurring payments and refunds to the original method.'),(581.8,'Wallet and bank payouts, with account validation before credit.'),(602.8,'Real-time payment confirmation by webhook for acceptance and payout.')]:
 region(18,(63,y,284,y+21),t,8.5,leading=10.5)
for y,t in [(550.8,'Acceptance and payout under Simpaisa or partner licences, by market.'),(571.8,'Multi-rail routing with failover.'),(582.8,'Prefunded payout balances; settlement in the agreed merchant currency.'),(603.8,'Reconciliation files, dedicated account management and 24/7 L1 support.')]:
 region(18,(323.5,y,545,y+(10 if y==571.8 else 21)),t,8.5,leading=10.5)
block(18,'Collect and pay out for 880m','Local acceptance, with payouts where supported',w=491)
block(18,'Wallet, account and domestic-card payers','Connect local checkout and supported payouts through one API, with settlement in the agreed merchant currency and one reconciliation file.',size=9.2,w=491)
region(18,(312,725,410,748),'24/7',15,'PH',WHITE,align='center',clear=(331,725,386,748))
region(18,(313,749,410,761),'L1 operational support',6.6,color=WHITE,align='center')

exact(8,'READING THE MAP','SIMPAISA COVERAGE',width=150)

# Remove the unsupported method count while preserving the metric-card layout.
region(2,(176,499.2,289,522),'Local',16,'PH',BLUE,align='center',clear=(221,498,243,523))
region(16,(185,725.25,285,747),'Local',15,'PH',WHITE,align='center',clear=(225,724,246,747))

# Update contents without changing its structure or page numbering.
for old,new in [('Overview','Simpaisa and our network'),('Our Relevant Use Cases','How businesses use Simpaisa'),('Built for Scale. Engineered for Trust','How payments move through Simpaisa'),('Market readiness at a glance','Payment landscape and Simpaisa coverage'),('Remittance corridors','Remittance receive markets'),('Let’s connect — more markets',"Let's connect more markets.")]:
 exact(3,old,new,width=425)
block(3,'Wallet growth in Pakistan','Wallet growth and local payment indicators across seven markets.',w=424)
block(3,'The seven markets compared','Market indicators and Simpaisa acceptance, disbursement and remittance coverage.',w=424)
block(3,'Inbound flows into five','Reported inflows into five receive markets and how local payout works.',w=424)

# Remove em dashes and typographic dash variants from any remaining text spans.
for n in range(1,20):
 for s in spans(n):
  if any(c in s['text'] for c in ['\u2014','\u2013','\u2011']):
   r=fitz.Rect(s['bbox'])
   if any(r.intersects(fitz.Rect(o['clear'])) for o in ops[n-1]):continue
   col=tuple(((s['color']>>k)&255)/255 for k in (16,8,0));f='PH' if 'Poppins' in s['font'] else 'IB' if 'Semi' in s['font'] or 'Bold' in s['font'] else 'IR'
   region(n,r,clean(s['text']),s['size'],f,col)

def wrap(text,font,size,width):
 out=[]
 for para in text.split('\n'):
  line=''
  for word in para.split():
   candidate=(line+' '+word).strip()
   if font.text_length(candidate,fontsize=size)<=width+.05:line=candidate
   else:
    if not line:raise ValueError(('word too long',word,width,size))
    out.append(line);line=word
  out.append(line)
 return out

for i,page in enumerate(doc):
 for op in ops[i]:
  r=fitz.Rect(op['clear']);page.add_redact_annot(r,fill=False,cross_out=False)
 # Keep all artwork, rules, gradients and logos intact.
 if ops[i]:page.apply_redactions(images=0,graphics=0,text=0)
 for name,path in [('IR','Inter.ttf'),('IB','InterSemi.ttf'),('PH','Poppins.ttf')]:page.insert_font(fontname=name,fontfile=str(HERE/'fonts'/path))
 for op in ops[i]:
  r=fitz.Rect(op['rect']);font=FONTS[op['font']];size=op['size'];leading=op['leading']
  if op['fill'] is not None:page.draw_rect(fitz.Rect(op['clear']),color=None,fill=op['fill'],overlay=True)
  if not op['text']:continue
  lines=wrap(op['text'],font,size,r.width)
  h=(len(lines)-1)*leading+size*(font.ascender-font.descender)
  # Never silently shrink to hide an overflow.
  if h>r.height+2.5:raise ValueError(('OVERFLOW',i+1,op['text'],r,len(lines),h))
  for j,line in enumerate(lines):
   y=r.y0+font.ascender*size+j*leading;x=r.x0
   if op['align']=='center':x+=(r.width-font.text_length(line,fontsize=size))/2
   page.insert_text((x,y),line,fontname=op['font'],fontsize=size,color=op['color'],overlay=True)
  logs.append({'page':i+1,'text':op['text'],'rect':op['rect'],'size':size})

doc[16].draw_rect(fitz.Rect(125,412,125+72*20.9/41.6,422),color=None,fill=BLUE,radius=.2)

# Add navigation and direct source links using existing visible labels.
titles=['Simpaisa Network Playbook','The playbook at a glance','Contents','Simpaisa and our network','How businesses use Simpaisa','How payments move through Simpaisa','The Gap We Close','Payment landscape and Simpaisa coverage','Pakistan','Bangladesh','Nepal','Iraq','Egypt','Saudi Arabia','Nigeria','Acceptance across the network','Remittance receive markets','Going live across the network',"Let's connect more markets."]
doc.set_toc([[1,t,i+1] for i,t in enumerate(titles)])
for i in range(3,19):
 for r in doc[2].search_for(titles[i]):doc[2].insert_link({'kind':fitz.LINK_GOTO,'from':r,'page':i,'to':fitz.Point(0,0)})
for p in doc:
 for r in p.search_for('www.simpaisa.com'):
  if not any(fitz.Rect(l['from']).intersects(r) for l in p.get_links()):p.insert_link({'kind':fitz.LINK_URI,'from':r,'uri':'https://www.simpaisa.com/'})
sources={9:'https://www.sbp.org.pk/psd/pdf/PS-Review-Q3FY26.pdf',10:'https://www.bb.org.bd/pub/annual/psdreport/paymentreport_dec2025.pdf',11:'https://www.nrb.org.np/psd/payment-systems-oversight-report-2081-82-2024-2025/',12:'https://cbi.iq/news/view/3087',13:'https://www.cbe.org.eg/ar/news-publications/news/2025/11/17/12/40/hassan-abdalla-pafix-2025',14:'https://www.sama.gov.sa/en-US/EconomicReports/MonthlyStatistics/Monthly_Bulletin_Dec_2025.pdf',15:'https://nibss-plc.com.ng/case-study-regulation-is-becoming-nigerias-fintech-advantage/'}
for n,url in sources.items():
 for r in doc[n-1].search_for('Sources:'):doc[n-1].insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(r.x0,r.y0,555,r.y1),'uri':url})
remittance_sources=[
'https://www.sbp.org.pk/press-release?department=PRESS&circular_start_date=2026-07-01&circular_end_date=2026-07-31',
'https://www.bb.org.bd/en/index.php/econdata/bop_remittance/2',
'https://www.nrb.org.np/red/current-macroeconomic-and-financial-situation-english-based-on-annual-data-of-2025-26/',
'https://www.cbe.org.eg/en/news-publications/news/2026/02/23/11/17/remittances-from-egyptians-working-abroad-record-usd-41%2C-d-%2C5-billion-during-2025',
'https://www.cbn.gov.ng/Out/2025/CCD/CBN%20UPDATE%20APRIL%202025.pdf']
for y,end,url in zip(ys,ends,remittance_sources):
 doc[16].insert_link({'kind':fitz.LINK_URI,'from':fitz.Rect(125,y,254,end),'uri':url})
for r in doc[9].search_for('March 2025 | selected schemes'):
 doc[9].insert_link({'kind':fitz.LINK_URI,'from':r,'uri':'https://www.bb.org.bd/pub/monthly/creditcard/march%2C%202025.pdf'})
limit_sources={
9:'https://www.sbp.org.pk/circulars/disd-circular-letter-no-02-of-2022',
10:'https://www.bkash.com/index.php/en/help/limits',
11:'https://www.nrb.org.np/category/faqs/faq_payment-system/faq_psd-others/page/2/',
12:'https://cbi.iq/static/uploads/up/file-167074229317374.pdf',
13:'https://www.cbe.org.eg/en/payment-systems-and-services/instant-payment-network',
14:'https://www.sama.gov.sa/en-us/payment/pages/Sarie.aspx',
15:'https://www.cbn.gov.ng/Out/2024/TED/Revised%20IMTO%20Guidelines%20-%20January%2C%202024.pdf'}
for n,url in limit_sources.items():
 for k,r in enumerate(doc[n-1].search_for('Limits')):
  target=url
  if n==9 and k!=1:target='https://www.sbp.org.pk/bprd/2026/CL9-Consolidated-Customer-Onboarding-Framework.pdf'
  if n==15 and k==1:target='https://www.cbn.gov.ng/out/2022/ccd/circular%20nip%20limit.pdf'
  if n==15 and k==0:continue
  doc[n-1].insert_link({'kind':fitz.LINK_URI,'from':r,'uri':target})
doc.set_metadata({'title':'Simpaisa Network Playbook 2026','author':'Simpaisa','subject':'Local payment methods across seven markets','keywords':'Simpaisa, payments, acceptance, disbursements, remittance','creator':'Simpaisa document production','producer':'PyMuPDF'})
doc.save(DEST,garbage=4,deflate=True)
(DEST.parent/'revision-log.json').write_text(json.dumps(logs,indent=2))
print(DEST);print(len(logs),'revised text regions')
