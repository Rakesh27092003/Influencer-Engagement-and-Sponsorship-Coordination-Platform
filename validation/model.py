from flask_sqlalchemy import SQLAlchemy
db=SQLAlchemy()

class influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # New field for name
    username = db.Column(db.String(60), nullable=False, unique=True)
    password = db.Column(db.String(40), nullable=False)
    category = db.Column(db.String(60), nullable=True)  # New field for category
    reach = db.Column(db.Integer, nullable=True)  # New field for reach
    followers = db.Column(db.Integer, nullable=True)  # New field for followers
    flag_status=db.Column(db.String)
    
class sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), nullable=False, unique=True)
    password = db.Column(db.String(40), nullable=False)
    category = db.Column(db.String(40), nullable=False)
    company_name = db.Column(db.String(100), nullable=False)
    budget = db.Column(db.Float, nullable=False)
    campaigns = db.relationship('campaigns', backref='sponsor', lazy=True)
    flag_status=db.Column(db.String)
    

    

class campaigns(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    campaign_name=db.Column(db.String(60),nullable=False)
    campaign_des=db.Column(db.String(200),nullable=False)
    campaign_status=db.Column(db.String(10),nullable=False)
    campaign_category=db.Column(db.String,nullable=False)
    campaign_sdate=db.Column(db.Integer,nullable=False)
    campaign_edate=db.Column(db.Integer,nullable=False)
    flag_status=db.Column(db.String)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    


class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    payment = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Pending')  # New column for status
    sponsor = db.relationship('sponsor', backref=db.backref('ad_requests', lazy=True))
    influencer = db.relationship('influencer', backref=db.backref('ad_requests', lazy=True))
    campaign = db.relationship('campaigns', backref=db.backref('ad_requests', lazy=True))
    
    
    
class AdRequestByInfluencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaigns.id'), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    payment = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='Pending')
    sponsor = db.relationship('sponsor', backref=db.backref('ad_requests_by_influencer', lazy=True))
    influencer = db.relationship('influencer', backref=db.backref('ad_requests_by_influencer', lazy=True))
    campaign = db.relationship('campaigns', backref=db.backref('ad_requests_by_influencer', lazy=True))