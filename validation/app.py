from flask import Flask,render_template, request,redirect, url_for,session,session, flash, jsonify
from model import db , influencer as influencer_model,sponsor as sponsor_model,campaigns as campaigns ,AdRequest as AdRequest_model,AdRequestByInfluencer as AdRequestByInfluencermodal

app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db1.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your_secret_key'

db.init_app(app)

with app.app_context():
    db.create_all()
    
@app.route("/")
def home():
    return render_template("home.html")

@app.route("/influencer_register", methods=['GET', 'POST'])
def influencer_register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        password = request.form['password']
        category = request.form['category']
        reach = request.form['reach']
        followers = request.form['followers']

        new_influencer = influencer_model(
            name=name,
            username=username,
            password=password,
            category=category,
            reach=reach,
            followers=followers
        )
        db.session.add(new_influencer)
        db.session.commit()

        return redirect(url_for('user'))

    return render_template("Influencer_signup.html")



@app.route("/sponsor_register", methods=['GET', 'POST'])
def sponsorregister():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        company_name = request.form['company_name']
        budget = request.form['budget']
        category = request.form['category']

        new_sponsor = sponsor_model(
            username=username,
            password=password,
            company_name=company_name,
            budget=budget,
            category=category
        )
        db.session.add(new_sponsor)
        db.session.commit()

        return redirect(url_for('user'))

    return render_template("Sponser_signup.html")

USER_CREDENTIALS = {
    'Rakesh': '123'
}
            
            
            
@app.route('/adminlogin', methods=['GET', 'POST'])
def adminlogin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        
        if username in USER_CREDENTIALS and USER_CREDENTIALS[username] == password:
    
            return redirect(url_for('admindash', username=username))
        else:
            
            return render_template('adminlogin.html', error='Invalid username or password')
    return render_template('adminlogin.html')
    

@app.route('/userlogin', methods=['POST'])
def userlogin():
    username = request.form['username'] 
    password = request.form['password']

    influencer = influencer_model.query.filter_by(username=username, password=password).first()
    sponsor = sponsor_model.query.filter_by(username=username, password=password).first()

    if influencer:
        if influencer.flag_status == 'Flagged':
            return "Your account is flagged"
        session['user'] = influencer.username
        session['role'] = 'influencer'
        return redirect(url_for('influencer_dashboard', influencer_id=influencer.id))
    elif sponsor:
        if sponsor.flag_status == 'Flagged':
            return "Your account is flagged"
        session['user'] = sponsor.username
        session['role'] = 'sponsor'
        return redirect(url_for('sponsordash', username=sponsor.username))
    else:
        return "Invalid username or password"

    

@app.route("/user")
def user():
    return render_template("userlogin.html")

@app.route("/admin")
def admin():
    return render_template("adminlogin.html")




























#-----------------------------admin---------------------------------------------------------------------------------------

@app.route('/admindash')
def admindash():
    flagged_campaigns = campaigns.query.filter_by(flag_status='flagged').all()
    unflagged_campaigns = campaigns.query.filter((campaigns.flag_status.is_(None)) | (campaigns.flag_status != 'flagged')).all()
    
    # Calculate counts
    total_campaigns = campaigns.query.count()
    total_sponsors = sponsor_model.query.count()
    total_influencers = influencer_model.query.count()
    
    return render_template(
        'admindash.html',
        flagged_campaigns=flagged_campaigns,
        unflagged_campaigns=unflagged_campaigns,
        total_campaigns=total_campaigns,
        total_sponsors=total_sponsors,
        total_influencers=total_influencers
    )

@app.route('/findadmin_influencer', methods=['GET', 'POST'])
def findadmin_influencer():
    query = request.form.get('query', '')
    category_filter = request.form.get('category', '')
    reach_min = request.form.get('reach_min', '')
    reach_max = request.form.get('reach_max', '')
    followers_min = request.form.get('followers_min', '')
    followers_max = request.form.get('followers_max', '')

    # Get unique categories from Campaign class
    categories = db.session.query(campaigns.campaign_category).distinct().all()
    categories = [cat[0] for cat in categories]

    # Start with the base query
    influencers = influencer_model.query

    # Apply name filter if present
    if query:
        influencers = influencers.filter(influencer_model.name.ilike(f'%{query}%'))

    # Apply category filter if present
    if category_filter:
        influencers = influencers.filter(influencer_model.category.ilike(f'%{category_filter}%'))

    # Apply reach filter if present
    if reach_min:
        influencers = influencers.filter(influencer_model.reach >= int(reach_min))
    if reach_max:
        influencers = influencers.filter(influencer_model.reach <= int(reach_max))

    # Apply followers filter if present
    if followers_min:
        influencers = influencers.filter(influencer_model.followers >= int(followers_min))
    if followers_max:
        influencers = influencers.filter(influencer_model.followers <= int(followers_max))

    # Execute the query
    influencers = influencers.all()

    return render_template('findadmin_influencer.html', influencers=influencers, query=query,
                           category_filter=category_filter, reach_min=reach_min, reach_max=reach_max,
                           followers_min=followers_min, followers_max=followers_max,
                           categories=categories)

@app.route('/flag_influencer/<int:influencer_id>', methods=['POST'])
def flag_influencer(influencer_id):
    influencer = influencer_model.query.get(influencer_id)
    if influencer:
        influencer.flag_status = 'Flagged'
        db.session.commit()
        flash('Influencer has been flagged.', 'success')
    else:
        flash('Influencer not found.', 'danger')
    
    return redirect(url_for('findadmin_influencer'))

@app.route('/unflag_influencer/<int:influencer_id>', methods=['POST'])
def unflag_influencer(influencer_id):
    influencer = influencer_model.query.get(influencer_id)
    if influencer:
        influencer.flag_status = None  # Clear the flag status
        db.session.commit()
        flash('Influencer has been unflagged.', 'success')
    else:
        flash('Influencer not found.', 'danger')
    
    return redirect(url_for('findadmin_influencer'))


@app.route('/findadmin_sponsor', methods=['GET', 'POST'])
def findadmin_sponsor():
    query = request.form.get('query', '')
    if request.method == 'POST' and query:
        sponsors = sponsor_model.query.filter(sponsor_model.company_name.ilike(f'%{query}%')).all()
    else:
        sponsors = sponsor_model.query.all()
    
    return render_template('findadmin_sponsor.html', sponsors=sponsors, query=query)

@app.route('/flag_sponsor/<int:sponsor_id>', methods=['POST'])
def flag_sponsor(sponsor_id):
    sponsor = sponsor_model.query.get_or_404(sponsor_id)
    sponsor.flag_status = 'Flagged'
    db.session.commit()
    return redirect(url_for('findadmin_sponsor'))

@app.route('/unflag_sponsor/<int:sponsor_id>', methods=['POST'])
def unflag_sponsor(sponsor_id):
    sponsor = sponsor_model.query.get_or_404(sponsor_id)
    sponsor.flag_status = ''
    db.session.commit()
    return redirect(url_for('findadmin_sponsor'))


@app.route('/findadmin_campaign', methods=['GET', 'POST'])
def findadmin_campaign():
    if request.method == 'POST':
        query = request.form.get('query', '')
        campaign = campaigns.query.filter(campaigns.campaign_name.like(f'%{query}%')).all()
    else:
        campaign = campaigns.query.all()

    return render_template('findadmin_campaigns.html', campaigns=campaign)


@app.route('/flag_campaign/<int:campaign_id>', methods=['POST'])
def flag_campaign(campaign_id):
    campaign = campaigns.query.get(campaign_id)
    if campaign:
        campaign.flag_status = 'Flagged'
        db.session.commit()
    return redirect(url_for('findadmin_campaign'))

@app.route('/unflag_campaign/<int:campaign_id>', methods=['POST'])
def unflag_campaign(campaign_id):
    campaign = campaigns.query.get(campaign_id)
    if campaign:
        campaign.flag_status = None
        db.session.commit()
    return redirect(url_for('findadmin_campaign'))

@app.route('/stat_admin')
def dashboard():
    return render_template('stat_admin.html')

@app.route('/statistics_data')
def statistics_data():
    influencer_count = influencer_model.query.count()
    sponsor_count = sponsor_model.query.count()
    
    data = {
        'labels': ['Influencers', 'Sponsors'],
        'data': [influencer_count, sponsor_count]
    }
    return jsonify(data)

@app.route('/deleteadmin_campaign/<int:campaign_id>', methods=['POST'])
def deleteadmin_campaign(campaign_id):
    campaign = campaigns.query.get_or_404(campaign_id)

    # Delete associated ad requests in both AdRequest and AdRequestByInfluencer models
    AdRequest_model.query.filter_by(campaign_id=campaign_id).delete()
    AdRequestByInfluencermodal.query.filter_by(campaign_id=campaign_id).delete()

    # Delete the campaign
    db.session.delete(campaign)
    db.session.commit()

    flash('Campaign and associated ad requests deleted successfully', 'success')
    return redirect(url_for('findadmin_campaign'))






























#--------------------------------------------------sponsor-----------------------------------------------------------------------------------------
@app.route("/sponsordash/<username>")
def sponsordash(username):
    sponsor = sponsor_model.query.filter_by(username=username).first_or_404()

    # Get all accepted ad requests for this sponsor
    ad_requests = AdRequest_model.query.filter_by(sponsor_id=sponsor.id, status='Accepted').all()
    ad_requests_by_influencer = AdRequestByInfluencermodal.query.filter_by(sponsor_id=sponsor.id, status='Accepted').all()

    # Extract campaign IDs from the accepted ad requests
    campaign_ids = {ad_request.campaign_id for ad_request in ad_requests}
    campaign_ids.update(ad_request.campaign_id for ad_request in ad_requests_by_influencer)

    # Query campaigns based on the extracted campaign IDs
    accepted_campaigns = campaigns.query.filter(campaigns.id.in_(campaign_ids)).all()

    # Prepare data for the ongoing campaigns
    campaigns_with_details = []
    for campaign in accepted_campaigns:
        campaign_sponsor = sponsor_model.query.get(campaign.sponsor_id)
        ad_request_details = [ad_request for ad_request in ad_requests if ad_request.campaign_id == campaign.id]
        ad_request_by_influencer_details = [ad_request for ad_request in ad_requests_by_influencer if ad_request.campaign_id == campaign.id]
        
        # Get the influencer details
        for ad_request in ad_request_details + ad_request_by_influencer_details:
            ad_request.influencer = influencer_model.query.get(ad_request.influencer_id)
        
        campaigns_with_details.append({
            'campaign': campaign,
            'sponsor_username': campaign_sponsor.username if campaign_sponsor else 'Unknown',
            'ad_requests': ad_request_details,
            'ad_requests_by_influencer': ad_request_by_influencer_details
        })

    # Get all pending ad requests by influencers for this sponsor
    pending_requests_by_influencer = AdRequestByInfluencermodal.query.filter_by(sponsor_id=sponsor.id, status='Pending').all()

    return render_template("sponsordash.html", sponsor=sponsor, campaigns=campaigns_with_details, influencer_requests=pending_requests_by_influencer)




@app.route("/update_request_status/<int:request_id>/<string:status>")
def update_request_status(request_id, status):
    # Validate status
    if status not in ['Accepted', 'Rejected']:
        return redirect(url_for('sponsordash', username=sponsor_model.username))

    # Fetch the ad request by ID
    ad_request = AdRequestByInfluencermodal.query.get_or_404(request_id)
    ad_request.status = status

    # Commit changes to the database
    db.session.commit()

    return redirect(url_for('sponsordash', username=ad_request.sponsor.username))

@app.route("/findsponsor/<username>")
def findsponsor(username):
    sponsor = sponsor_model.query.filter_by(username=username).first_or_404()
    return render_template("findsponsor.html",sponsor=sponsor)

@app.route('/campaign/<username>', methods=['GET', 'POST'])
def campaign(username):
    user = sponsor_model.query.filter_by(username=username).first_or_404()

    if request.method == 'POST':
        campaign_name = request.form['campaign_name']
        campaign_des = request.form['campaign_des']
        campaign_status = request.form['campaign_status']
        campaign_category = request.form['campaign_category']
        campaign_sdate = request.form['campaign_sdate']
        campaign_edate = request.form['campaign_edate']

        new_campaign = campaigns(
            campaign_name=campaign_name,
            campaign_des=campaign_des,
            campaign_status=campaign_status,
            campaign_category=campaign_category,
            campaign_sdate=campaign_sdate,
            campaign_edate=campaign_edate,
            sponsor_id=user.id
        )
        db.session.add(new_campaign)
        db.session.commit()
        flash('Campaign created successfully!', 'success')
        return redirect(url_for('campaign', username=username))

    user_campaigns = campaigns.query.filter_by(sponsor_id=user.id).all()
    return render_template('campaign.html', user=user, campaigns=user_campaigns)



@app.route('/campaigns/<username>')
def campaigns_page(username):
    user = sponsor_model.query.filter_by(username=username).first_or_404()
    campaignsvar = campaigns.query.filter_by(sponsor_id=user.id).all()
    return render_template('campaign.html', user=user, campaigns=campaignsvar)





@app.route('/delete_campaign/<username>', methods=['POST'])
def delete_campaign(username):
    campaign_id = request.form['campaign_id']
    campaign = campaigns.query.get(campaign_id)

    if campaign:
        # Delete all ad requests related to the campaign in the AdRequest table
        AdRequest_model.query.filter_by(campaign_id=campaign_id).delete()
        
        # Delete all ad requests related to the campaign in the AdRequestByInfluencer table
        AdRequestByInfluencermodal.query.filter_by(campaign_id=campaign_id).delete()
        
        # Delete the campaign
        db.session.delete(campaign)
        db.session.commit()

    return redirect(url_for('campaign', username=username))










@app.route('/edit_campaign/<username>', methods=['POST'])
def edit_campaign(username):
    campaign_id = request.form['campaign_id']
    campaign = campaigns.query.get(campaign_id)

    if campaign:
        campaign.campaign_name = request.form['campaign_name']
        campaign.campaign_des = request.form['campaign_des']
        campaign.campaign_status = request.form['campaign_status']
        campaign.campaign_category = request.form['campaign_category']
        campaign.campaign_sdate = request.form['campaign_sdate']
        campaign.campaign_edate = request.form['campaign_edate']

        db.session.commit()

    return redirect(url_for('campaign',username=username))









@app.route('/sponsor/dashboard/<username>', methods=['GET', 'POST'])
def sponsor_find(username):
    sponsor = sponsor_model.query.filter_by(username=username).first()
    search_results = None
    name = request.form.get('name', '')
    niche = request.form.get('niche', '')
    min_reach = request.form.get('min_reach', 0, type=int)
    min_followers = request.form.get('min_followers', 0, type=int)

    # Query unique niches
    unique_niches = db.session.query(influencer_model.category).distinct().all()
    unique_niches = [niche[0] for niche in unique_niches]

    if request.method == 'POST':
        if 'see_all' in request.form:
            # Display all influencers without filter
            search_results = influencer_model.query.all()
        else:
            # Display influencers based on filters
            search_results = influencer_model.query.filter(
                influencer_model.name.ilike(f'%{name}%'),
                influencer_model.category.ilike(f'%{niche}%'),
                influencer_model.reach >= min_reach,
                influencer_model.followers >= min_followers
            ).all()
    else:
        # Default behavior: show all influencers
        search_results = influencer_model.query.all()

    return render_template('findsponsor.html', sponsor=sponsor, search_results=search_results, name=name, niche=niche, min_reach=min_reach, min_followers=min_followers, unique_niches=unique_niches)


@app.route('/ad_request/<username>', methods=['POST'])
def ad_request(username):
    influencer_id = request.form['influencer_id']
    sponsor = sponsor_model.query.filter_by(username=username).first()

    # Fetch all campaigns that the sponsor has
    all_campaigns = campaigns.query.filter_by(sponsor_id=sponsor.id).all()

    # Fetch campaign IDs already requested by the influencer in both tables
    existing_campaign_ids = set(
        [ar.campaign_id for ar in AdRequest_model.query.filter_by(sponsor_id=sponsor.id, influencer_id=influencer_id).all()] +
        [ar.campaign_id for ar in AdRequestByInfluencermodal.query.filter_by(sponsor_id=sponsor.id, influencer_id=influencer_id).all()]
    )

    # Filter out campaigns that are already requested or flagged
    available_campaigns = [
        campaign for campaign in all_campaigns
        if campaign.id not in existing_campaign_ids and (not campaign.flag_status or campaign.flag_status != 'Flagged')
    ]

    return render_template('ad_request.html', sponsor=sponsor, influencer_id=influencer_id, campaigns=available_campaigns)







@app.route('/submit_ad_request', methods=['POST',"GET"])
def submit_ad_request():
    sponsor_id = request.form['sponsor_id']
    influencer_id = request.form['influencer_id']
    campaign_id = request.form['campaign_id']
    message = request.form['message']
    payment = request.form['payment']

    # Save the ad request to the database
    ad_request = AdRequest_model(
        sponsor_id=sponsor_id,
        influencer_id=influencer_id,
        campaign_id=campaign_id,
        message=message,
        payment=payment
    )
    db.session.add(ad_request)
    db.session.commit()
    flash('Request was sent successfully!')
    return redirect(url_for('sponsor_find', username=sponsor_model.query.get(sponsor_id).username))



@app.route('/new_ad_request/<username>/<int:campaign_id>', methods=['GET', 'POST'])
def new_ad_request(username, campaign_id):
    sponsor = sponsor_model.query.filter_by(username=username).first()
    if sponsor is None:
        return "Sponsor not found", 404

    campaign = campaigns.query.get(campaign_id)
    if campaign is None:
        return "Campaign not found", 404

    ad_requests = AdRequest_model.query.join(influencer_model, AdRequest_model.influencer_id == influencer_model.id)\
        .filter(AdRequest_model.sponsor_id == sponsor.id, AdRequest_model.campaign_id == campaign_id)\
        .add_columns(AdRequest_model.id, AdRequest_model.payment, AdRequest_model.message, AdRequest_model.status, influencer_model.name.label('influencer_name'))\
        .all()

    return render_template('ad_request_display.html', username=username, campaign_id=campaign_id, campaign_name=campaign.campaign_name, ad_requests=ad_requests)




@app.route('/delete_ad_request/<int:ad_request_id>', methods=['POST'])
def delete_ad_request(ad_request_id):
    ad_request = AdRequest_model.query.get_or_404(ad_request_id)
    db.session.delete(ad_request)
    db.session.commit()
    flash('Ad request deleted successfully', 'success')
    return redirect(request.referrer)

@app.route('/edit_ad_request/<int:ad_request_id>', methods=['POST'])
def edit_ad_request(ad_request_id):
    ad_request = AdRequest_model.query.get_or_404(ad_request_id)
    ad_request.message = request.form['message']
    ad_request.payment = request.form['payment']
    db.session.commit()
    flash('Ad request updated successfully', 'success')
    return redirect(request.referrer)

@app.route('/campaign_statistics_data')
def campaign_statistics_data():
    flagged_count = db.session.query(db.func.count(campaigns.id)).filter(campaigns.flag_status == 'Flagged').scalar()
    unflagged_count = db.session.query(db.func.count(campaigns.id)).filter(campaigns.flag_status == None).scalar()

    campaign_count = {
        'labels': ['Flagged', 'Unflagged'],
        'data': [flagged_count, unflagged_count]
    }
    return jsonify(campaign_count)


@app.route('/statistics/<username>')
def sponsor_statistics(username):
    sponsor_data = sponsor_model.query.filter_by(username=username).first()
    
    if not sponsor_data:
        return "Sponsor not found", 404

    # Fetch data for AdRequest and AdRequestByInfluencer
    ad_requests = AdRequest_model.query.filter_by(sponsor_id=sponsor_data.id).all()
    ad_requests_by_influencer = AdRequestByInfluencermodal.query.filter_by(sponsor_id=sponsor_data.id).all()
    
    # Count status occurrences
    ad_request_status_counts = {}
    ad_request_by_influencer_status_counts = {}
    
    for request in ad_requests:
        status = request.status
        ad_request_status_counts[status] = ad_request_status_counts.get(status, 0) + 1
    
    for request in ad_requests_by_influencer:
        status = request.status
        ad_request_by_influencer_status_counts[status] = ad_request_by_influencer_status_counts.get(status, 0) + 1

    data = {
        'ad_request_labels': list(ad_request_status_counts.keys()),
        'ad_request_data': list(ad_request_status_counts.values()),
        'ad_request_by_influencer_labels': list(ad_request_by_influencer_status_counts.keys()),
        'ad_request_by_influencer_data': list(ad_request_by_influencer_status_counts.values())
    }
    
    return render_template('sponsor_stat.html', username=username, data=data)











































#-----------------------------------------------------influencer------------------------------------------------------------------------------------

@app.route("/infludash/<username>")
def infludash(username):
    influencer = influencer_model.query.filter_by(username=username).first_or_404()
    return redirect(url_for('influencer_dashboard',influencer=influencer))

@app.route("/influprofile/<string:username>")
def influprofile(username):
    influencer = influencer_model.query.filter_by(username=username).first_or_404()
    return render_template("influprofile.html", influencer=influencer)

@app.route('/update_profile/<int:influencer_id>', methods=['POST'])
def update_profile(influencer_id):
    influencer = influencer_model.query.get(influencer_id)
    if influencer:
        influencer.name = request.form['name']
        influencer.category = request.form['category']
        influencer.reach = request.form['reach']
        influencer.followers = request.form['followers']
        
        
        db.session.commit()
        return redirect(url_for('influprofile', username=influencer.username))
    return redirect(url_for('influprofile', username=influencer.username))


@app.route('/findinflu/<int:influencer_id>', methods=['GET', 'POST'])
def findinflu(influencer_id):
    influencer = influencer_model.query.get_or_404(influencer_id)

    # Get filter criteria from the request
    filter_name = request.args.get('filter_name', '')
    filter_category = request.args.get('filter_category', '')

    # Find all campaign IDs that have an ad request sent by the influencer in either AdRequestByInfluencer or AdRequest
    requested_campaign_ids = db.session.query(AdRequestByInfluencermodal.campaign_id).filter_by(influencer_id=influencer_id).union(
        db.session.query(AdRequest_model.campaign_id).filter_by(influencer_id=influencer_id)
    ).all()
    requested_campaign_ids = [id for (id,) in requested_campaign_ids]

    # Query all public campaigns excluding the ones that have been requested
    public_campaigns_query = campaigns.query.filter(~campaigns.id.in_(requested_campaign_ids))

    # Apply filters if provided
    if filter_name:
        public_campaigns_query = public_campaigns_query.filter(campaigns.campaign_name.ilike(f'%{filter_name}%'))
    if filter_category:
        public_campaigns_query = public_campaigns_query.filter(campaigns.campaign_category.ilike(f'%{filter_category}%'))

    public_campaigns = public_campaigns_query.all()

    # Get sponsor usernames for the filtered campaigns
    campaigns_with_sponsors = []
    for campaign in public_campaigns:
        sponsor = sponsor_model.query.get(campaign.sponsor_id)
        campaigns_with_sponsors.append({
            'campaign': campaign,
            'sponsor_username': sponsor.username if sponsor else 'Unknown'
        })

    # Get unique categories for the dropdown
    categories = db.session.query(campaigns.campaign_category).distinct().all()
    categories = [category[0] for category in categories]

    return render_template('findinflu.html', influencer=influencer, campaigns=campaigns_with_sponsors, filter_name=filter_name, filter_category=filter_category, categories=categories)


@app.route('/request_ad/<int:campaign_id>', methods=['GET', 'POST'])
def request_ad(campaign_id):
    influencer_id = request.args.get('influencer_id')
    sponsor_id = request.args.get('sponsor_id')

    influencer = influencer_model.query.get_or_404(influencer_id)
    campaign = campaigns.query.get_or_404(campaign_id)
    sponsor = sponsor_model.query.get_or_404(sponsor_id)

    if request.method == 'POST':
        message = request.form['message']
        payment = request.form['payment']

        new_ad_request = AdRequestByInfluencermodal(
            sponsor_id=sponsor.id,
            influencer_id=influencer.id,
            campaign_id=campaign.id,
            message=message,
            payment=payment
        )

        db.session.add(new_ad_request)
        db.session.commit()

        flash('Ad request submitted successfully!', 'success')
        return redirect(url_for('findinflu', influencer_id=influencer.id))

    return render_template('request_ad.html', campaign=campaign, influencer=influencer, sponsor=sponsor)


@app.route('/influencer_dashboard/<int:influencer_id>')
def influencer_dashboard(influencer_id):
    influencer = influencer_model.query.get_or_404(influencer_id)
    
    # Fetch only pending ad requests
    ad_requests = AdRequest_model.query.filter_by(influencer_id=influencer_id, status='Pending').all()
    
    # Fetch accepted ad requests to get active campaigns
    accepted_requests = AdRequest_model.query.filter_by(influencer_id=influencer_id, status='Accepted').all()
    
    # Extract unique campaign IDs from accepted requests
    campaign_ids = [request.campaign_id for request in accepted_requests]
    
    # Get the campaigns with these IDs
    active_campaigns = campaigns.query.filter(campaigns.id.in_(campaign_ids)).all()
    
    return render_template('infludash.html', influencer=influencer, ad_requests=ad_requests, active_campaigns=active_campaigns)






@app.route('/accept_ad_request/<int:influencer_id>/<int:ad_request_id>', methods=['POST'])
def accept_ad_request(influencer_id, ad_request_id):
    ad_request = AdRequest_model.query.get(ad_request_id)
    if ad_request:
        ad_request.status = 'Accepted'
        db.session.commit()
    return redirect(url_for('influencer_dashboard', influencer_id=influencer_id))

@app.route('/reject_ad_request/<int:influencer_id>/<int:ad_request_id>', methods=['POST'])
def reject_ad_request(influencer_id, ad_request_id):
    ad_request = AdRequest_model.query.get(ad_request_id)
    if ad_request:
        ad_request.status = 'Rejected'
        db.session.commit()
    return redirect(url_for('influencer_dashboard', influencer_id=influencer_id))


















@app.route('/infl_statistics/<username>')
def influencer_statistics(username):
    influencer_data = influencer_model.query.filter_by(username=username).first()
    
    if not influencer_data:
        return "Influencer not found", 404

    # Fetch data for AdRequest and AdRequestByInfluencer
    ad_requests = AdRequest_model.query.filter_by(influencer_id=influencer_data.id).all()
    ad_requests_by_influencer = AdRequestByInfluencermodal.query.filter_by(influencer_id=influencer_data.id).all()
    
    # Count status occurrences
    ad_request_status_counts = {}
    ad_request_by_influencer_status_counts = {}
    
    for request in ad_requests:
        status = request.status
        ad_request_status_counts[status] = ad_request_status_counts.get(status, 0) + 1
    
    for request in ad_requests_by_influencer:
        status = request.status
        ad_request_by_influencer_status_counts[status] = ad_request_by_influencer_status_counts.get(status, 0) + 1

    data = {
        'ad_request_labels': list(ad_request_status_counts.keys()),
        'ad_request_data': list(ad_request_status_counts.values()),
        'ad_request_by_influencer_labels': list(ad_request_by_influencer_status_counts.keys()),
        'ad_request_by_influencer_data': list(ad_request_by_influencer_status_counts.values())
    }
    
    return render_template('influencer_stat.html', influencer=influencer_data, data=data)








@app.route('/requests/<username>')
def requests_page(username):
    # Fetch the influencer by username
    influencer = influencer_model.query.filter_by(username=username).first_or_404()

    # Fetch all ad requests for this influencer
    ad_requests = AdRequestByInfluencermodal.query.filter_by(influencer_id=influencer.id).all()

    return render_template('requests_page.html', ad_requests=ad_requests, influencer=influencer)


from flask import request, redirect, url_for

@app.route('/delete_request/<int:ad_request_id>', methods=['POST'])
def delete_request(ad_request_id):
    ad_request = AdRequestByInfluencermodal.query.get_or_404(ad_request_id)
    db.session.delete(ad_request)
    db.session.commit()
    # Redirect to the referrer URL (previous page)
    return redirect(request.referrer or url_for('requests_page', username='some_username'))
  # Redirect to the requests page or another page as needed



app.run(debug=True) 