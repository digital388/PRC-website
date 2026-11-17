"""
Default copy for every editable text slot on the site.
Keys are grouped by page: <page>.<slot>. The seed_content command imports
these into the PageText model so they become editable at /admin/.
"""

PAGE_TEXT_DEFAULTS = {
    # ---------- Home ----------
    "home.hero_title": {"en": "Informing Discourse | Shaping Debate", "np": "संवादलाई सूचित | बहसलाई आकार"},
    "home.hero_title_2": {"en": "Ideas For Accountable Governance", "np": "जवाफदेही शासनका लागि विचार"},
    "home.about_heading": {"en": "About Us", "np": "हाम्रोबारे"},
    "home.about_body": {
        "en": "Pokhara Research Center (PRC), is a not-for-profit distributing institution registered in the year 2019. PRC defines itself as a public policy research institute with the aspiration of developing into a leading thinktank and an institution of excellence in Nepal. The centre was established as a unique response to the changing political climate in Nepal. Through research, public dialogue, and collaboration, PRC brings evidence and diverse perspectives into policy discussions. Its work focuses on strengthening accountable governance and connecting citizens, policymakers, and institutions.",
        "np": "पोखरा रिसर्च सेन्टर (PRC) सन् २०१९ मा दर्ता भएको नाफा वितरण नगर्ने संस्था हो। PRC ले आफूलाई सार्वजनिक नीति अनुसन्धान संस्थाका रूपमा स्थापित गर्दै नेपालकै अग्रणी थिङ्क ट्याङ्क तथा उत्कृष्टताको केन्द्रका रूपमा विकास गर्ने लक्ष्य राखेको छ। नेपालको बदलिँदो राजनीतिक परिवेशको विशिष्ट आवश्यकतालाई सम्बोधन गर्ने उद्देश्यले यस केन्द्रको स्थापना गरिएको हो। अनुसन्धान, सार्वजनिक संवाद र सहकार्यमार्फत PRC ले नीतिगत छलफलमा प्रमाणमा आधारित तथ्य तथा विविध दृष्टिकोणहरू समावेश गर्दछ। यसका कार्यहरू जवाफदेही शासन प्रणाली सुदृढ बनाउने तथा नागरिक, नीतिनिर्माता र संस्थाहरूबीच सम्बन्ध स्थापित गर्ने कुरामा केन्द्रित छन्।",
    },
    "home.gallery_heading": {"en": "Our Work in Pictures", "np": "तस्बिरहरूमा हाम्रो काम"},
    "home.journey_heading": {"en": "From Vision to Institution", "np": "दृष्टिबाट संस्थासम्म"},
    "home.journey_body": {
        "en": "Pokhara Research Centre began its journey in 2017, marking the year of germination when the idea and foundational work were initiated. From 2017 to 2019, PRC underwent its incubation phase - refining its vision, building networks, and doing preparatory work. In May 2019, it was formally registered, transitioning from concept to a recognized institution. Since then, PRC has grown as a public-policy think tank focused on provincial affairs, based in Kaski district of Gandaki Province.",
        "np": "पोखरा रिसर्च सेन्टरले आफ्नो यात्रा २०१७ मा सुरु गर्यो, जुन सङ्केतको वर्ष हो, जब यसको विचार र आधारभूत कार्य सुरु भएको थियो। २०१७ देखि २०१९ सम्म PRC ले आफ्नो विकास चरण व्यवस्थापन गर्दै दृष्टिकोण परिष्कार गर्न, सञ्जाल निर्माण गर्न र तयारी कार्य गर्न भयो। मे २०१९ मा यसको औपचारिक दर्ता भई यो एक अवधारणाबाट स्थापित संस्थामा परिवर्तन भयो। त्यसपछि PRC ले प्रादेशिक मामिलामा केन्द्रित सार्वजनिक नीति विचार प्रतिष्ठानको रूपमा विकास पाउँदै आएको छ, जुन गण्डकी प्रदेशको कास्की जिल्लामा अवस्थित छ।",
    },
    "home.mission_heading": {"en": "Our Mission", "np": "हाम्रो उद्देश्य"},
    "home.mission_body": {
        "en": "Our mission is to strengthen Nepal's federalism by promoting provincial autonomy, reducing centralization, and informing citizens through research, programs, and strategic communication.",
        "np": "हाम्रो उद्देश्य प्रादेशिक स्वायत्तता प्रवर्द्धन, केन्द्रीकरण न्यूनीकरण, र अनुसन्धान, कार्यक्रम तथा रणनीतिक सञ्चारमार्फत नागरिकलाई सूचित गर्दै नेपालको संघीयतालाई सुदृढ बनाउनु हो।",
    },
    "home.vision_heading": {"en": "Our Vision", "np": "हाम्रो दृष्टिकोण"},
    "home.vision_body": {
        "en": "A democratic Nepal with empowered subnational governments and a well-informed electorate.",
        "np": "सशक्त उपराष्ट्रिय सरकारहरू र सुसूचित मतदाता वर्ग भएको लोकतान्त्रिक नेपाल।",
    },
    "home.objectives_heading": {"en": "Our Core Values", "np": "हाम्रा मूल्यमान्यताहरू"},
    "home.objective_1": {"en": "Independence : Maintain nonpartisanship, intellectual and financial autonomy.", "np": "स्वतन्त्रता: गैरदलीयता कायम राख्दै बौद्धिक तथा आर्थिक स्वायत्तता सुनिश्चित गर्ने।"},
    "home.objective_2": {"en": "Inclusivity: Gender parity in participation and positions of authority.", "np": "समावेशिता: सहभागिता तथा नेतृत्वदायी पदहरूमा लैङ्गिक समानता सुनिश्चित गर्ने।"},
    "home.objective_3": {"en": "Integrity: Uphold transparency, quality assurance, and ethical standards in all work.", "np": "निष्ठा: सबै कार्यमा पारदर्शिता, गुणस्तर सुनिश्चितता तथा नैतिक मापदण्डहरू कायम राख्ने।"},
    "home.objective_4": {"en": "Collaboration: Constructive partnerships with government, civil society, academia, and development partners.", "np": "सहकार्य: सरकार, नागरिक समाज, प्राज्ञिक क्षेत्र तथा विकास साझेदारहरूसँग रचनात्मक साझेदारी स्थापित गर्ने।"},
    "home.objective_5": {"en": "Public Benefit: Address gaps in capacity development or research to analyse and report on current issues for public benefit.", "np": "सार्वजनिक हित: सार्वजनिक हितका लागि समसामयिक मुद्दाहरूको विश्लेषण तथा प्रतिवेदन गर्न अनुसन्धान र क्षमता विकासका क्षेत्रमा रहेका रिक्तताहरू सम्बोधन गर्ने।"},
    "home.objective_6": {"en": "Innovation: Sustainable state-of-art development of mission based deliverables.", "np": "नवप्रवर्तन: संस्थाको उद्देश्यअनुरूपका उपलब्धिहरू हासिल गर्न दिगो तथा अत्याधुनिक विकासका उपायहरू अवलम्बन गर्ने।"},

    # ---------- Institution ----------
    "institution.hero_title": {"en": "Collaboration | Policy Innovation", "np": "सहयोग | नीतिगत नवप्रवर्तन"},
    "institution.mission_heading": {"en": "Institution Cell", "np": "संस्थागत सेल"},
    "institution.mission_body": {
        "en": "In December 2017, two years after the promulgation of the Constitution of Nepal, Sujan Regmi, the Co-founder of the institution, recognizing the gap in development policy in Nepal and realizing the rights bestowed by the constitution began the incubation exercise. This led to the creation of the first cell namely, Institution cell with the objective of formulating the center's identity, public profile, processes and stakeholder relations.",
        "np": "नेपाल तथा विश्वस्तरमा उत्कृष्ट अनुसंन्धान कम्पनीका रूपमा पोखरा रिसर्च सेन्टर लाई स्थापित गर्नु यस सेलको मुख्य उद्देश्य हो। उच्च गुणस्तरको, प्रमाण–आधारित अनुसन्धान तथा कार्यान्वयनयोग्य नीतिगत सिफारिसहरू उत्पादन गर्दै लोकतान्त्रिक शासन प्रणालीलाई सुदृढ बनाउने, सार्वजनिक क्षेत्रको कार्यसम्पादन सुधार गर्ने, निजी उद्यमलाई प्रवर्द्धन गर्ने तथा समावेशी सामाजिक–आर्थिक विकासमा योगदान पुर्‍याउने यस सेलको लक्ष्य हो। गहन विश्लेषण र विश्वसनीय ज्ञान उत्पादनमार्फत यस सेलले सक्षम सार्वजनिक संस्था निर्माण र सचेत मतदाता तयार पार्न सहयोग पुर्‍याउँछ, साथै गुणस्तरीय रोजगारी सिर्जनामा योगदान गर्दछ।",
    },
    "institution.projects_heading": {"en": "Our Projects", "np": "हाम्रा परियोजनाहरू"},
    "institution.team_heading": {"en": "Team Members", "np": "टिम सदस्यहरू"},
    "institution.partners_heading": {"en": "Our Patrons", "np": "हाम्रा साझेदारहरू"},
    "institution.funding_heading": {"en": "How We Are Funded", "np": "हामी कसरी कोष प्राप्त गर्छौं"},
    "institution.funding_general_heading": {"en": "General sources of funding", "np": "सामान्य कोषका स्रोतहरू"},
    "institution.funding_general_body": {"en": "Recurring support that keeps our work running", "np": "हाम्रो काम चलायमान राख्ने आवर्ती सहयोग"},
    "institution.funding_project_heading": {"en": "Project based grants", "np": "परियोजना आधारित अनुदान"},
    "institution.funding_project_body": {"en": "Time-bound funding tied to specific research and programs", "np": "विशिष्ट अनुसन्धान तथा कार्यक्रमसँग सम्बन्धित समयबद्ध कोष"},

    # ---------- Province ----------
    "province.hero_title": {"en": "Decentralizing Power | Responsive Governance", "np": "सत्ता विकेन्द्रीकरण | उत्तरदायी शासन"},
    "province.mission_heading": {"en": "Province Cell", "np": "प्रदेश सेल"},
    "province.mission_body_1": {
        "en": "In 2019, PRC was formally registered in its namesake Pokhara Metropolitan City in Kaski district of Gandaki Province. The YO Strategic Directive led by the Institution Cell, was enacted to create the first project cell namely, Province Cell with the mission to promote economic freedom of the individual through good governance in the provinces.",
        "np": "पोखरा रिसर्च सेन्टरको 'प्रदेश सेल'ले अनुसन्धान, नीति विश्लेषण र सरोकारवालासँगको संवादमार्फत प्रादेशिक स्वायत्तताको पक्षपोषण गर्दै नेपालमा विकेन्द्रीकृत, समावेशी र उत्तरदायी शासन प्रणालीको प्रवर्द्धन गर्दछ। स्थानीय स्तरका समाधानद्वारा निर्देशित दिगो विकास र पारदर्शी नीतिगत प्रणाली सुनिश्चित गर्न यो सेलले स्थानीय संस्थाहरू एवं नागरिकको सशक्तीकरणमा जोड दिन्छ।",
    },
    "province.mission_body_2": {
        "en": "The primary objective of the Province cell is to reduce excessive centralization in Nepal and enhance provincial autonomy with the aim to bring the government closer to citizens. The Province Cell dissects its work in three wings pursuant to the three facets of provincial governance in Nepal, namely, Province Assembly (inc. 2019), Province Government (inc. 2021) and Intergovernmental Relations (inc. 2023).",
        "np": "प्रदेश सेलको प्रमुख उद्देश्य नेपालमा अत्यधिक केन्द्रीकरण घटाउने र प्रादेशिक स्वायत्तता बढाउने हो, जसले सरकारलाई नागरिकसँग नजिक ल्याउँछ। प्रदेश सेलले आफ्नो कामलाई नेपालको प्रादेशिक शासनका तीन पक्षअनुसार तीन विभागमा विभाजन गर्छ, अर्थात् प्रदेश सभा (स्था. २०१९), प्रदेश सरकार (स्था. २०२१) र अन्तर–सरकारी सम्बन्ध (स्था. २०२३)।",
    },
    "province.flagship_heading": {"en": "Our Flagship Programs", "np": "हाम्रा प्रमुख कार्यक्रमहरू"},
    "province.projects_heading": {"en": "Past Projects", "np": "सम्पन्न परियोजनाहरू"},

    # ---------- Constitution ----------
    "constitution.hero_title": {"en": "Well Informed Electorate | Civic Action", "np": "सुसूचित मतदाता वर्ग | नागरिक सक्रियता"},
    "constitution.mission_heading": {"en": "Constitution Cell", "np": "संविधान सेल"},
    "constitution.mission_body": {
        "en": "In September 2025, witnessing the \"Gen-Z Protests\" in the country and releasing the gap in public knowledge on constitutional freedoms and rights, the Institution cell created the Constitution Cell with the aim of creating a well informed electorate through periodic citizen engagement deliverables in a series of events celebrating the freedoms of the Nepalese Constitution annually.",
        "np": "नवीन कार्यक्रम, अनुभवजन्य अनुसन्धान तथा रणनीतिक ज्ञान प्रसारमार्फत राजनीतिक तथा संवैधानिक प्रक्रियामा नागरिकको अर्थपूर्ण सहभागिता विस्तार गर्नु यस सेलको उद्देश्य हो। समावेशी सहभागिताका अवसरहरू सिर्जना गर्दै नागरिकलाई नीति निर्माण प्रक्रिया बुझ्न, प्रभाव पार्न र सह–निर्माण गर्न सक्षम बनाइन्छ। यस सेलले नागरिकहरू आफ्ना जीवनमा प्रत्यक्ष प्रभाव पार्ने निर्णयहरूमा सक्रिय भूमिका खेल्ने, सूचित, संलग्न र सहकार्यपूर्ण नागरिक संस्कृतिको विकास गर्दै लोकतान्त्रिक शासन प्रणालीलाई सुदृढ बनाउन प्रतिबद्धता जनाउँछ।",
    },
    "constitution.programs_heading": {"en": "From Our Programs", "np": "हाम्रा कार्यक्रमहरूबाट"},
    "constitution.exhibition_heading": {"en": "Virtual Exhibition", "np": "भर्चुअल प्रदर्शनी"},
    "constitution.exhibition_body": {"en": "Click below for the Virtual Exhibition on Metasteps 3D Immersive Experience.", "np": "मेटास्टेप्स थ्रीडी इमर्सिभ अनुभवमा भर्चुअल प्रदर्शनीको लिङ्क"},
    "constitution.projects_heading": {"en": "Projects", "np": "परियोजनाहरू"},

    # ---------- Events ----------
    "events.hero_title": {"en": "Events", "np": "कार्यक्रमहरू"},
    "events.empty_text": {"en": "No events in this category.", "np": "यो श्रेणीमा कुनै कार्यक्रम छैन।"},

    # ---------- YPG Fellowship ----------
    "ypg.hero_title": {"en": "Youth In Policy | Governance Fellowship", "np": "नीतिमा युवा | सुशासन फेलोसिप"},
    "ypg.about_heading": {"en": "Youth In Policy & Governance (YPG) Fellowship Program", "np": "नीति तथा सुशासनमा युवा (वाईपीजी) फेलोसिप कार्यक्रम"},
    "ypg.about_body": {
        "en": "Our flagship fellowship that equips young Nepali leaders with the skills, exposure, and mentoring to engage with provincial policy. Across multiple cohorts, fellows gain hands-on research experience, take part in youth assemblies, and work directly with lawmakers — building a pipeline of informed, capable leaders for stronger provincial governance.",
        "np": "हाम्रो प्रमुख फेलोसिप कार्यक्रम, जसले युवा नेपाली नेतृत्वकर्ताहरूलाई प्रदेश नीतिमा सहभागी हुनका लागि सीप, अभ्यास र मार्गदर्शन प्रदान गर्दछ। विभिन्न समूहहरूमा फेलोहरूले व्यावहारिक अनुसन्धान अनुभव प्राप्त गर्छन्, युवा सभाहरूमा भाग लिन्छन् र प्रत्यक्ष रूपमा विधायकहरूसँग काम गर्छन् — सुदृढ प्रादेशिक सुशासनका लागि जानकार र सक्षम नेतृत्वकर्ताहरूको शृङ्खला निर्माण गर्दै।",
    },
    "ypg.milestones_heading": {"en": "Milestones", "np": "उपलब्धिहरू"},
    "ypg.fellows_heading": {"en": "Our Fellows", "np": "हाम्रा फेलोहरू"},
    "ypg.testimonials_heading": {"en": "Fellows' Voices", "np": "फेलोहरूको आवाज"},
    "ypg.cohorts_heading": {"en": "Fellowship Cohorts", "np": "फेलोसिप समूहहरू"},

    # ---------- Support Us ----------
    "support.hero_title": {"en": "Support Us", "np": "हामीलाई सहयोग गर्नुहोस्"},

    # ---------- Publications / Archives ----------
    "publications.hero_title": {"en": "Publications", "np": "प्रकाशनहरू"},
    "archives.hero_title": {"en": "Archives", "np": "अभिलेख"},

    # ---------- Navigation & footer ----------
    "nav.menu_label": {"en": "Menu", "np": "मेनु"},
    "nav.close_label": {"en": "Close", "np": "बन्द"},
    "footer.tagline": {
        "en": "A public policy research institute based in Pokhara, working to inform discourse and shape debate for accountable governance in Gandaki Province and beyond.",
        "np": "पोखरामा आधारित सार्वजनिक नीति अनुसन्धान संस्था, गण्डकी प्रदेश र त्यसबाहिर जवाफदेही शासनका लागि संवादलाई सूचित र बहसलाई आकार दिन काम गर्दै।",
    },
}
