import json
import re

from django.shortcuts import render
from django.http import Http404
from django.templatetags.static import static
from django.urls import reverse

from .models import (
    TeamMember, BoardMember, Partner, InstitutionProject, FundingItem, ProvinceProject,
    FlagshipProgram, YPGBatch, PastProject, YPGFellow, YPGFellowProfile, YPGTestimonial,
    Event, Publication, BlogPost, GalleryPhoto,
)
from .ypg_fellows_data import YPG_FELLOWS_DATA
from .project_record_data import PROJECT_RECORD

# Content cloned from https://www.pokharacentre.org/

TEAM = [
    {
        "slug": "sujan-regmi",
        "np_name": "सुजन रेग्मी", "en_name": "Sujan Regmi",
        "role_np": "कार्यकारी निर्देशक", "role_en": "Executive Director",
        "title_en": "Executive Director",
        "title_np": "कार्यकारी निर्देशक",
        "bio_en": "Sujan leads PRC as its Executive Director. Since PRC’s inception, he has been instrumental in informing debate and shaping dialogue on the state of public policy implementation in Nepal. He directs the Programs and Outreach Divisions of the company designing and executing format based dialogue and consultation series with elected representatives across four Provincial Assemblies as well as running youth skill development programs to train future public leaders.",
        "bio_np": "सुजन रेग्मीले पोखरा रिसर्च सेन्टरको कार्यकारी निर्देशकको रूपमा नेतृत्व प्रदान गर्दै आएका छन्। सेन्टरको स्थापनाकालदेखि नै उनले नेपालमा सार्वजनिक नीति कार्यान्वयनको अवस्थाबारे सार्थक बहस र संरचित संवाद निर्माणमा महत्वपूर्ण भूमिका खेलेका छन्। उनको नेतृत्वमा कार्यक्रम तथा पहुँच (Programs and Outreach) विभाग सञ्चालन हुँदै आएको छ, जसअन्तर्गत नेपालका चारवटा प्रदेश सभामा निर्वाचित जनप्रतिनिधिहरूसँग प्रारूप–आधारित संवाद तथा परामर्श शृंखलाहरू डिजाइन र कार्यान्वयन गरिन्छ। साथै, उनले भविष्यका सार्वजनिक नेतृत्व निर्माण गर्ने उद्देश्यले युवा सीप विकास तथा क्षमता अभिवृद्धि कार्यक्रमहरूको पनि नेतृत्व गर्छन्।",
    },
    {
        "slug": "kuldeep-niraula",
        "np_name": "डा. कुलदीप निरौला", "en_name": "Kuldeep Niraula Ph.D",
        "role_np": "अनुसन्धान सल्लाहकार", "role_en": "Research Advisor",
        "title_en": "Research Advisor",
        "title_np": "अनुसन्धान सल्लाहकार",
        "bio_en": "Kuldeep Niraula, Ph.D. in Conflict Analysis and Resolution from George Mason University’s Carter School for Peace and Conflict Resolution, USA, serves as a Research Advisor at Pokhara Research Centre, advising on the centre’s research agenda and publications. He contributes to the development of research proposals and provides technical inputs to ongoing research projects. He also proactively contributes to institutional narrative writing, working both independently and collaboratively with the research team.",
        "bio_np": "डा. कुलदीप निरौला (जर्ज मेसन युनिभर्सिटी, कार्टर स्कुल फर पिस एन्ड कन्फ्लिक्ट रिजोलुसन, अमेरिका, द्वन्द्व विश्लेषण तथा समाधानमा विद्यावारिधि), पोखरा रिसर्च सेन्टरमा अनुसन्धान सल्लाहकारका रूपमा कार्यरत हुनुहुन्छ। उहाँले केन्द्रको अनुसन्धान तथा प्रकाशनसम्बन्धी कार्यमा सल्लाह दिनुका साथै अनुसन्धान प्रस्ताव तयार गर्न र अनुसन्धान परियोजनाहरूमा प्राविधिक सहयोग प्रदान गर्नुहुन्छ। साथै, उहाँ संस्थागत लेखनमा पनि सक्रिय रूपमा संलग्न रहँदै अनुसन्धान टिमसँग स्वतन्त्र तथा सहकार्यात्मक रूपमा कार्य गर्नुहुन्छ।",
    },
    {
        "slug": "laxmi-sharma",
        "np_name": "लक्ष्मी शर्मा", "en_name": "Laxmi Sharma",
        "role_np": "अनुसन्धान, तालिम तथा परियोजना सल्लाहकार", "role_en": "Advisor - Research, Training and Project",
        "title_en": "Advisor - Research, Training and Project",
        "title_np": "अनुसन्धान, तालिम तथा परियोजना सल्लाहकार",
        "bio_en": "Laxmi Sharma, an educator, teacher trainer, and researcher from Pokhara, Nepal, serves as an Advisor: Research, Training and Projects at Pokhara Research Centre. A PhD scholar at Kathmandu University School of Education and a 2027 Fulbright TEA grantee, she brings experience in research methodology, teacher professional development, and designing and facilitating training on leadership, gender inclusion, well-being, sustainability, and digital skills. Her research focuses on digital transformation, green skills, educational governance, and teacher development.",
        "bio_np": "लक्ष्मी शर्मा पोखरा, नेपालकी शिक्षाविद्, शिक्षक प्रशिक्षक तथा अनुसन्धानकर्ता हुनुहुन्छ। उहाँ पोखरा रिसर्च सेन्टरमा अनुसन्धान, तालिम तथा परियोजना सल्लाहकारका रूपमा कार्यरत हुनुहुन्छ। उहाँ काठमाडौं विश्वविद्यालय, स्कुल अफ एजुकेसनमा विद्यावारिधि (PhD) अध्ययनरत हुनुका साथै सन् २०२७ का लागि फुलब्राइट टीईए (Fulbright TEA) कार्यक्रमकी छनोट प्राप्त सहभागी हुनुहुन्छ। उहाँसँग अनुसन्धान पद्धति, शिक्षकको व्यावसायिक विकास तथा नेतृत्व, लैङ्गिक समावेशिता, कल्याण, दिगोपन र डिजिटल सीपसम्बन्धी तालिमको डिजाइन तथा सहजीकरणमा अनुभव छ। उहाँको अनुसन्धानका प्रमुख क्षेत्रहरूमा डिजिटल रूपान्तरण, हरित सीप, शैक्षिक सुशासन तथा शिक्षक विकास पर्दछन्।",
    },
    {
        "slug": "annapurna-adhikari",
        "np_name": "अन्नपूर्णा अधिकारी", "en_name": "Annapurna Adhikari",
        "role_np": "संस्थाको किचन इन्चार्ज", "role_en": "Incharge - Administration",
        "title_en": "Incharge - Administration",
        "title_np": "संस्थाको किचन इन्चार्ज",
        "bio_en": "Annapurna manages the Kitchen and Housekeeping duties of the Centre ensuring an enabling environment for its employees and visitors. She is also responsible for procurement, preparation, budgeting and reporting for the Kitchen providing a hearty home cooked Nepali lunch for twelve to twenty five people on any given day.",
        "bio_np": "अन्नपूर्णा अधिकारीले केन्द्रको भान्सा तथा हाउसकिपिङ व्यवस्थापन गर्दै कर्मचारी तथा आगन्तुकका लागि सुरक्षित, स्वच्छ र सहयोगी कार्य–वातावरण सुनिश्चित गर्छिन्। उनी भान्सासम्बन्धी खरिद, तयारी, बजेट निर्माण तथा प्रतिवेदनको जिम्मेवारी सम्हाल्दै दैनिक रूपमा १२ देखि २५ जनासम्मका लागि घरायसी नेपाली भोजन व्यवस्थापन गर्छिन्।",
    },
    {
        "slug": "monika-ranabhat",
        "np_name": "मोनिका रानाभाट", "en_name": "Monika Ranabhat",
        "role_np": "अनुसन्धान फेलो", "role_en": "Research Fellow",
        "title_en": "Research Fellow",
        "title_np": "अनुसन्धान फेलो",
        "bio_en": "Monika advises the Institution Cell on the various products, programs and projects of the centre’s mission-based cells with a special focus on gender parity initiatives in the workplace. As a research advisor she also facilitates policy research on provincial affairs, public policy and institutional reform.",
        "bio_np": "मोनिकाले सेन्टरको मिसन–आधारित सेलहरूका विभिन्न उत्पादन, कार्यक्रम र परियोजनाहरूका सम्बन्धमा संस्थागत सेल (Institution Cell) लाई सल्लाह प्रदान गर्दछिन्। यसमा कार्यस्थलमा लैंगिक समानता कायम गर्ने पहलहरूमा उनको विशेष जोड रहने गर्दछ। अनुसन्धान सल्लाहकारको रूपमा उनले प्रादेशिक मामिला, सार्वजनिक नीति र संस्थागत सुधारका क्षेत्रमा हुने नीतिगत अनुसन्धानमा समेत सहजीकरण गर्दछिन्।",
    },
    {
        "slug": "saurab-wagle",
        "np_name": "सौरब वाग्ले", "en_name": "Saurab Wagle",
        "role_np": "प्रबन्धक – वित्त", "role_en": "Manager - Finance",
        "title_en": "Manager - Finance",
        "title_np": "प्रबन्धक – वित्त",
        "bio_en": "Saurab Wagle serves as the Manager, Finance at Pokhara Research Centre. He oversees the Centre’s overall financial management, including budgeting, accounting, financial records, and documentation. He also manages the financial aspects of the Centre’s programmes and activities and supports administrative coordination and effective use of resources.",
        "bio_np": "सौरब वाग्ले सेन्टरमा वित्त प्रबन्धक का रूपमा कार्यरत छन्। उनले सेन्टरको समग्र वित्तीय व्यवस्थापनअन्तर्गत बजेट, लेखा, वित्तीय अभिलेख तथा कागजात व्यवस्थापन गर्छन्। साथै, उनी सेन्टरका कार्यक्रम तथा गतिविधिहरूको वित्तीय व्यवस्थापन, प्रशासनिक समन्वय तथा स्रोत–साधनको प्रभावकारी उपयोग सुनिश्चित गर्न सक्रिय रूपमा संलग्न छन्।",
    },
    {
        "slug": "binita-subedi",
        "np_name": "बिनिता सुवेदी", "en_name": "Binita Subedi",
        "role_np": "अनुसन्धान फेलो", "role_en": "Research Fellow",
        "title_en": "Research Fellow",
        "title_np": "अनुसन्धान फेलो",
        "bio_en": "Binita Subedi is a Research Fellow at Pokhara Research Centre. She has authored peer-reviewed publications on Nepal’s political economy, migration governance, and international economic relations. She holds a Master’s degree in International Relations and Diplomacy from Tribhuvan University. At PRC, she supports research initiatives, produces policy briefs and reports, and facilitates stakeholder consultations and policy dialogues.",
        "bio_np": "बिनिता सुवेदी पोखरा रिसर्च सेन्टरकी अनुसन्धान फेलो हुन्। उनले नेपालको राजनीतिक अर्थतन्त्र, आप्रवासन शासन र अन्तर्राष्ट्रिय आर्थिक सम्बन्धसम्बन्धी विषयमा सहकर्मी-समीक्षित अनुसन्धान लेखहरू प्रकाशित गरेकी छन्। उनले त्रिभुवन विश्वविद्यालयबाट अन्तर्राष्ट्रिय सम्बन्ध तथा कूटनीतिमा स्नातकोत्तर उपाधि हासिल गरेकी छन्। PRC मा उनी अनुसन्धानका पहलहरूमा सहयोग गर्ने, नीतिगत संक्षिप्तपत्र तथा प्रतिवेदनहरू तयार गर्ने र सरोकारवालाहरूसँगको परामर्श तथा नीतिगत संवादलाई सहजीकरण गर्ने कार्यमा संलग्न छिन्।",
    },
    {
        "slug": "shree-krishna-dhoj-basnet",
        "np_name": "श्री कृष्ण ध्वज बस्नेत", "en_name": "Shree Krishna Dhoj Basnet",
        "role_np": "सहायक – अनुसन्धान र कम्युनिकेशंस", "role_en": "Associate - Research & Communications",
        "title_en": "Associate - Research & Communications",
        "title_np": "सहायक–सहयोगी – अनुसन्धान र कम्युनिकेशंस",
        "bio_en": "Shree is the Communication Associate for the Province Cell, overseeing product development and the execution of key programs. He leads the efforts of the center’s Nepali Language Committee, focusing on grassroots outreach and effective community engagement fostering policy partnerships to strengthen communication between the center and its diverse stakeholders.",
        "bio_np": "श्रीकृष्ण ध्वज बस्नेत प्रदेश र संविधान सेलसँग आबद्ध सञ्चार सहयोगी हुन्, जसले सेन्टरका नीति-आधारित उत्पादन विकास र कार्यक्रम कार्यान्वयनमा सक्रिय योगदान पुर्‍याउँछन्। उनी सेन्टरको नेपाली भाषा समितिको नेतृत्व गर्दै स्थानीय तहसम्म प्रभावकारी सञ्चार र नीतिगत संवादलाई अघि बढाउँछन्। यस भूमिकामा उनले सेन्टर र विभिन्न सरोकारवालाहरूबीच रणनीतिक साझेदारी प्रवर्द्धन गर्न विशेष जोड दिन्छन्।",
    },
    {
        "slug": "suyasha-pun",
        "np_name": "सुयशा पुन", "en_name": "Suyasha Pun",
        "role_np": "सहायक – सञ्चार तथा प्रचार", "role_en": "Associate - Communications & Outreach",
        "title_en": "Associate - Communications & Outreach",
        "title_np": "सहायक–सहयोगी – सञ्चार तथा प्रचार",
        "bio_en": "Suyasha coordinates the engagement activities for the centre’s Province Cell’s stakeholders. She translates data driven research into communication briefs and outreach material enabling decisive policy dialogue and fostering inclusive participation across the execution of its programs. She also contributes towards the development of knowledge products for elected representatives in provincial assemblies.",
        "bio_np": "सुयशा पुनले सेन्टरको प्रदेश कोषिकासँग सम्बन्धित सरोकारवालासँगको संलग्नता तथा पहुँच गतिविधिहरूको समन्वय गर्छिन्। उनी डेटा–आधारित अनुसन्धानलाई नीतिगत सञ्चार सामग्री, संक्षेप (Briefs) र पहुँच सामग्रीमा रूपान्तरण गर्दै प्रभावकारी नीति संवाद र समावेशी सहभागिता सुनिश्चित गर्छिन्। साथै, प्रदेश सभाका निर्वाचित प्रतिनिधिहरूका लागि ज्ञान–आधारित सामग्री विकासमा पनि योगदान पुर्‍याउँछिन्।",
    },
    {
        "slug": "prabesh-subedi",
        "np_name": "प्रवेश सुवेदी", "en_name": "Prabesh Subedi",
        "role_np": "प्रबन्धक – कार्यक्रम तथा सञ्चार", "role_en": "Manager - Programs & Communications",
        "title_en": "Manager - Programs & Communications",
        "title_np": "प्रबन्धक – कार्यक्रम तथा सञ्चार",
        "bio_en": "Prabesh manages various projects of the centre’s programs division implementing its grant projects, actualising its products and leading partnership activities for different government and international grant programs. He additionally coordinates interconnected efforts, manages shared resources and ensures the collective impact by forging new partnerships across multiple interest groups in Nepal.",
        "bio_np": "प्रवेशले सेन्टरको कार्यक्रम विभागका विभिन्न परियोजनाहरूको व्यवस्थापन गर्दै अनुदान परियोजनाहरू कार्यान्वयन, संस्थागत उत्पादनहरूको प्रयोग तथा विभिन्न सरकारी एवं अन्तर्राष्ट्रिय अनुदान कार्यक्रमहरूका लागि साझेदारी गतिविधिको नेतृत्व गर्छन्। उनले अन्तरसम्बन्धित प्रयासहरूको समन्वय र साझा स्रोतहरूको व्यवस्थापन गर्छन् भने नेपालका विभिन्न सरोकारवाला समूहहरूसँग नयाँ साझेदारी निर्माणमार्फत सामूहिक प्रभाव सुनिश्चित गर्छन्।",
    },
    {
        "slug": "sankalpa-baral",
        "np_name": "संकल्प बराल", "en_name": "Sankalpa Baral",
        "role_np": "सहायक प्रबन्धक – कार्यक्रम तथा प्रचार", "role_en": "Associate Manager - Programs & Outreach",
        "title_en": "Associate Manager - Programs & Outreach",
        "title_np": "सहायक प्रबन्धक – कार्यक्रम तथा प्रचार",
        "bio_en": "Sankalpa manages the Programs Division of the centre implementing its grant projects, deploying its products and leading engagement activities for various stakeholders of the Province Cell. He additionally coordinates interconnected efforts, manages shared resources and ensures the collective impact through the centre’s social media presence.",
        "bio_np": "संकल्प बरालले केन्द्रको कार्यक्रम विभागको व्यवस्थापन गर्दै अनुदान परियोजनाहरू कार्यान्वयन, संस्थागत उत्पादनहरूको प्रयोग तथा प्रदेश कोषिकाका सरोकारवालासँग संलग्नता गतिविधिको नेतृत्व गर्छन्। उनी विभिन्न विभागबीच समन्वय, साझा स्रोत व्यवस्थापन तथा केन्द्रको सामाजिक सञ्जाल उपस्थितिमार्फत संस्थागत प्रभाव र पहुँच विस्तार सुनिश्चित गर्छन्।",
    },
    {
        "slug": "cimonika-ghimire",
        "np_name": "सिमोनिका घिमिरे", "en_name": "Cimonika Ghimire",
        "role_np": "सहायक – प्रशासन", "role_en": "Associate - Administration",
        "title_en": "Associate - Administration",
        "title_np": "सहायक – प्रशासन",
        "bio_en": "Cimonika assists the general administration of the centre maintaining efficient record management, daily financial log ensuring resource optimization and central administrative coordination. She additionally participates in ICT integration in office administration and financial record management.",
        "bio_np": "सिमोनिका घिमिरेले सेन्टरको सामान्य प्रशासनमा सहयोग गर्दै अभिलेख व्यवस्थापन, दैनिक वित्तीय अभिलेख तथा स्रोत–साधनको प्रभावकारी उपयोग सुनिश्चित गर्छिन्। साथै, उनी कार्यालय प्रशासन र वित्तीय प्रणालीमा सूचना तथा सञ्चार प्रविधि (ICT) एकीकरणका प्रयासमा सक्रिय रूपमा संलग्न हुन्छिन्।",
    },
    {
        "slug": "sujal-gurung",
        "np_name": "सुजल गुरुङ", "en_name": "Sujal Gurung",
        "role_np": "सहायक – प्रशासन", "role_en": "Associate - Administration",
        "title_en": "Associate - Administration",
        "title_np": "सहायक – प्रशासन",
        "bio_en": "Sujal assists the general administration of the centre enabling operational efficiency by operationalising procurement, maintaining supply chains and other such related activities. He also coordinates with several logistics partners, financial institutions and regulatory authorities.",
        "bio_np": "सुजल गुरुङले खरिद प्रक्रिया सञ्चालन, आपूर्ति शृंखला व्यवस्थापन तथा सम्बन्धित प्रशासनिक कार्यमार्फत सेन्टरको सञ्चालन दक्षता अभिवृद्धि गर्छन्। उनी विभिन्न ढुवानी साझेदार, वित्तीय संस्था तथा नियामक निकायसँग आवश्यक समन्वयको जिम्मेवारी पनि सम्हाल्छन्।",
    },
    {
        "slug": "samita-ghimire",
        "np_name": "समिता घिमिरे", "en_name": "Samita Ghimire",
        "role_np": "सहायक – अनुसन्धान तथा सञ्चार", "role_en": "Associate - Research & Communication",
        "title_en": "Associate - Research & Communication",
        "title_np": "सहायक – अनुसन्धान तथा सञ्चार",
        "bio_en": "She supports the Institution’s strategic and research initiatives by contributing to its impact agenda, ensuring the quality and relevance of institutional outputs, and assisting in research management and publications. She also co-manages development and strategy efforts, supports partnerships and fundraising initiatives, and represents the Institution in policy, academic, and stakeholder engagements.",
        "bio_np": "उहाँ संस्थाको प्रभावमुखी तथा अनुसन्धानसम्बन्धी कार्यहरूमा योगदान पुर्‍याउँदै संस्थागत उत्पादनहरूको गुणस्तर र सान्दर्भिकता सुनिश्चित गर्न सहयोग गर्नुहुन्छ। साथै, विकास तथा रणनीति सम्बन्धी कार्य, साझेदारी तथा स्रोत परिचालनका पहलहरूमा सहकार्य गर्दै नीतिगत, शैक्षिक तथा सरोकारवालासँगका विभिन्न कार्यक्रममा संस्थाको प्रतिनिधित्व गर्नुहुन्छ।",
    },
    {
        "slug": "sohan-thapa",
        "np_name": "सोहन थापा", "en_name": "Sohan Thapa",
        "role_np": "सहायक प्रबन्धक – सञ्चार", "role_en": "Associate Manager - Communications",
        "title_en": "Associate Manager - Communications",
        "title_np": "सहायक प्रबन्धक – सञ्चार",
        "bio_en": "Sohan Thapa participates in the production and management of various deliverables of PRC-Digital - the tech group that manages the various digital tools associated with one of three project divisions of the company: research, programs and communications. He assists in the development of ICT tools in Monitoring, Learning & Evaluation of project deliverables making efforts accessible, and measurable.",
        "bio_np": "सोहन थापाले सेन्टरको वेबसाइट तथा अनुसन्धान, कार्यक्रम र सञ्चार विभागसँग सम्बन्धित डिजिटल उपकरणहरूको व्यवस्थापन गर्छन्। उनले अनुगमन, सिकाइ तथा मूल्यांकन (Monitoring, Learning & Evaluation - MLE) का लागि ICT उपकरण विकासमा सहयोग गर्दै परियोजना परिणामहरूलाई अन्तरक्रियात्मक, पहुँचयोग्य र मापनयोग्य बनाउने काम गर्छन्।",
    },
    {
        "slug": "divya-pokhrel",
        "np_name": "दिव्या पोख्रेल", "en_name": "Divya Pokhrel",
        "role_np": "सहायक – कार्यक्रम तथा सञ्चार", "role_en": "Assistant - Program & Communications",
        "title_en": "Assistant - Program & Communications",
        "title_np": "सहायक – कार्यक्रम तथा सञ्चार",
        "bio_en": "Divya assists in the implementation and management of various deliverables within the Programs & Communications division—the group responsible for executing grant projects, actualising products, and maintaining partnerships. She supports the coordination of shared resources and interconnected efforts across different government and international programs, helping ensure the collective impact of the centre’s initiatives across multiple interest groups in Nepal.",
        "bio_np": "दिव्याले कार्यक्रम तथा सञ्चार विभाग अन्तर्गतका विभिन्न उपलब्धिहरूको कार्यान्वयन र व्यवस्थापनमा सहयोग पुर्‍याउँछिन्— जुन विभाग अनुदान आयोजनाहरूको सञ्चालन, उत्पादनहरूको बजारीकरण तथा प्रवर्द्धन, र साझेदारीहरू कायम राख्न जिम्मेवार छ। उनले विभिन्न सरकारी तथा अन्तर्राष्ट्रिय कार्यक्रमहरू बीच साझा स्रोतहरूको परिचालन र अन्तरसम्बन्धित प्रयासहरूको समन्वयमा सहयोग गर्दै नेपालका विभिन्न सरोकारवाला समूहहरूमा केन्द्रका प्रयासहरूको सामूहिक प्रभाव सुनिश्चित गर्न मद्दत गर्दछिन्।",
    },
]

def _category_for_role(role_en):
    """Sort a member into a section based on their role title."""
    role = (role_en or "").lower()
    if "advisor" in role or "adviser" in role:
        return TeamMember.Category.ADVISOR
    if "fellow" in role:
        return TeamMember.Category.RESEARCH_FELLOW
    return TeamMember.Category.EXECUTIVE


TEAM_PHOTOS = {
    "sujan-regmi": "website/images/team/t1.jpg",
    "kuldeep-niraula": "website/images/team/t2.jpg",
    "laxmi-sharma": "website/images/team/laxmi-sharma.png",
    "annapurna-adhikari": "website/images/team/t3.jpg",
    "monika-ranabhat": "website/images/team/t4.jpg",
    "saurab-wagle": "website/images/team/t5.jpg",
    "binita-subedi": "website/images/team/binita-subedi.jpg",
    "shree-krishna-dhoj-basnet": "website/images/team/t6.jpg",
    "suyasha-pun": "website/images/team/t7.jpg",
    "prabesh-subedi": "website/images/team/t8.jpg",
    "sankalpa-baral": "website/images/team/t9.jpg",
    "sohan-thapa": "website/images/team/t13.jpg",
    "cimonika-ghimire": "website/images/team/t10.jpg",
    "sujal-gurung": "website/images/team/t11.jpg",
    "samita-ghimire": "website/images/team/t12.jpg",
    "divya-pokhrel": "website/images/team/t14.jpg",
}

TEAM_ORDER = [
    "sujan-regmi", "kuldeep-niraula", "laxmi-sharma", "annapurna-adhikari",
    "monika-ranabhat", "saurab-wagle", "binita-subedi", "shree-krishna-dhoj-basnet",
    "suyasha-pun", "prabesh-subedi", "sankalpa-baral", "sohan-thapa",
    "cimonika-ghimire", "sujal-gurung", "samita-ghimire", "divya-pokhrel",
]

for _m in TEAM:
    _m.setdefault("category", _category_for_role(_m["role_en"]))
    _m.setdefault("photo", TEAM_PHOTOS.get(_m["slug"], ""))

TEAM.sort(key=lambda m: TEAM_ORDER.index(m["slug"]) if m["slug"] in TEAM_ORDER else len(TEAM_ORDER))

TEAM_BY_SLUG = {m["slug"]: m for m in TEAM}

TEAM_GROUPS = [
    (TeamMember.Category.EXECUTIVE, "Executive", "कार्यकारी"),
    (TeamMember.Category.ADVISOR, "Advisor", "सल्लाहकार"),
    (TeamMember.Category.RESEARCH_FELLOW, "Research Fellow", "अनुसन्धान फेलो"),
]

BOARD = [
    {"en_name": "Khem Raj Baral", "np_name": "खेमराज बराल",
     "role_en": "Member - Board of Directors", "role_np": "बोर्ड सदस्य"},
    {"en_name": "Kamala Khatri", "np_name": "कमला खत्री",
     "role_en": "Member - Board of Directors", "role_np": "बोर्ड सदस्य"},
    {"en_name": "Satish GC", "np_name": "सतीश जी.सी.",
     "role_en": "Member - Board of Directors", "role_np": "बोर्ड सदस्य"},
]

PARTNERS = [
    {"en": "The Samriddhi Foundation", "np": "समृद्धि फाउण्डेशन", "type_en": "National & Subnational", "type_np": "राष्ट्रिय र उप-राष्ट्रिय", "since": "A.D 2019", "logo": "website/images/partners/samriddhi.png"},
    {"en": "ATLAS Network", "np": "एटलस नेटवर्क", "type_en": "International", "type_np": "अन्तर्राष्ट्रिय", "since": "A.D 2019", "logo": "website/images/partners/atlas-network.svg"},
    {"en": "The United States Embassy in Kathmandu", "np": "अमेरिकी दूतावास, काठमाडौं", "type_en": "International", "type_np": "अन्तर्राष्ट्रिय", "since": "A.D 2019", "logo": "website/images/partners/us-embassy.webp"},
    {"en": "Gandaki Province Assembly Secretariat", "np": "गण्डकी प्रदेश सभा सचिवालय", "type_en": "Government", "type_np": "सरकारी", "since": "A.D 2019", "logo": "website/images/partners/gandaki-assembly.jpg"},
    {"en": "Centre for International Private Enterprise", "np": "सेन्टर फर इन्टरनेशनल प्राइभेट इन्टरप्राइज", "type_en": "International", "type_np": "अन्तर्राष्ट्रिय", "since": "A.D 2020", "logo": "website/images/partners/cipe.png"},
    {"en": "Prithvi Narayan Campus, Tribhivan University", "np": "पृथ्वीनारायण क्याम्पस, त्रिभुवन विश्वविद्यालय", "type_en": "Academia", "type_np": "शैक्षिक", "since": "A.D. 2020", "logo": "website/images/partners/prithvi-narayan-campus.png"},
    {"en": "Gandaki Province Planning Commission", "np": "गण्डकी प्रदेश नीति तथा योजना आयोग", "type_en": "Government", "type_np": "सरकारी", "since": "A.D. 2021", "logo": "website/images/partners/Gandaki Province Planning Commission.jpg"},
    {"en": "National Endowment for Democracy", "np": "नेशनल इन्डोमेन्ट फर डेमोक्रेसी", "type_en": "International", "type_np": "अन्तर्राष्ट्रिय", "since": "A.D 2021", "logo": "website/images/partners/ned.png"},
    {"en": "Hriti Foundation", "np": "ऋति फाउण्डेशन", "type_en": "National & Subnational", "type_np": "राष्ट्रिय र उप-राष्ट्रिय", "since": "A.D 2022", "logo": "website/images/partners/hriti.jpg"},
    {"en": "United Nations Development Program", "np": "संयुक्त राष्ट विकास कार्यक्रम", "type_en": "International", "type_np": "अन्तर्राष्ट्रिय", "since": "A.D 2023", "logo": "website/images/partners/undp.jpg"},
    {"en": "National Democratic Institute (NDI)", "np": "नेशनल डेमोक्रेटिक इन्स्टिच्युट", "type_en": "International", "type_np": "अन्तर्राष्ट्रिय", "since": "A.D 2023", "logo": "website/images/partners/NDI.png"},
    {"en": "Bikalpa - an alternative Foundation", "np": "विकल्प - एन अल्टरनेटिभ फाउण्डेशन", "type_en": "National & Subnational", "type_np": "राष्ट्रिय र उप-राष्ट्रिय", "since": "A.D 2023", "logo": "website/images/partners/bikalpa.png"},
    {"en": "The Asia Foundation", "np": "द एसिया फाउण्डेशन", "type_en": "International", "type_np": "अन्तर्राष्ट्रिय", "since": "A.D 2024", "logo": "website/images/partners/asia-foundation.png"},
    {"en": "Pokhara Metropolitan Corporation", "np": "पोखरा महानगरपालिका", "type_en": "Government", "type_np": "सरकारी", "since": "A.D. 2024", "logo": "website/images/partners/pmc.jpg"},
    {"en": "Business Promotion Centre, Kaski, Pokhara", "np": "व्यवसाय प्रवर्द्धन केन्द्र, कास्की, पोखरा", "type_en": "Government", "type_np": "सरकारी", "since": "A.D. 2024", "logo": "website/images/partners/bpc.png"},
    {"en": "Institute of Agriculture and Animal Sciences, Lamjung Campus, Tribhuvan University", "np": "कृषि र पशु विज्ञान अध्ययन संस्थान लमजुङ क्याम्पस, त्रिभुवन विश्वविद्यालय", "type_en": "Academia", "type_np": "शैक्षिक", "since": "A.D 2025", "logo": "website/images/partners/lamjung-campus.png"},
    {"en": "College of Natural Resource Management, Agriculture Forest University", "np": "प्राकृतिक स्रोत व्यवस्थापन कलेज, कृषि तथा वन विज्ञान विश्वविद्यालय", "type_en": "Academia", "type_np": "शैक्षिक", "since": "A.D 2025", "logo": "website/images/partners/College of Natural Resource Management, Agriculture Forest University.jpg"},
    {"en": "Gandaki University", "np": "गण्डकी विश्वविद्यालय", "type_en": "Academia", "type_np": "शैक्षिक", "since": "A.D 2025", "logo": "website/images/partners/gandaki-university.png"},
    {"en": "Pokhara University", "np": "पोखरा विश्वविद्यालय", "type_en": "Academia", "type_np": "शैक्षिक", "since": "A.D. 2025", "logo": "website/images/partners/pokhara-university.png"},
    {"en": "Gandaki Province Training Academy", "np": "गण्डकी प्रदेश प्रशिक्षण प्रतिष्ठान", "type_en": "Government", "type_np": "सरकारी", "since": "A.D 2025", "logo": "website/images/partners/gpta.jpg"},
    {"en": "Ministry of Agriculture and Land Management", "np": "कृषि तथा भूमि व्यवस्था मन्त्रालय", "type_en": "Government", "type_np": "सरकारी", "since": "A.D. 2025", "logo": "website/images/partners/ministry-agriculture.jpg"},
    {"en": "Nepalese Young Entrepreneurs Forum, Pokhara Chapter", "np": "नेप्लिज योङ इन्टरप्रेन्योर्स फोरम, पोखरा च्याप्टर", "type_en": "Provincial", "type_np": "प्रादेशीक", "since": "A.D. 2026", "logo": "website/images/partners/nyef.png"},
]

INSTITUTION_PROJECTS = [
    {
        "title": "MYOP", "type": "Five year strategic plan",
        "description": "The Multi-Year Operational Plan actualises an outcomes based approach to producing results. The MYOP 2026-2030's central theme takes inspiration from the Constitution of Nepal (Preamble): ELIMINATING all forms of discrimination and oppression resulted from all feudalistic, autocratic, centralized, unitary, system of governance of the State.",
        "title_np": "एम.वाई.ओ.पी.", "type_np": "५ वर्षे प्रशासनिक योजना",
        "description_np": "बहुवर्षीय कार्य योजनाले (MYOP) तथ्यमा आधारित दृष्टिकोणलाई वास्तविकतामा रूपान्तरण गर्दछ। MYOP २०२६-२०३० को केन्द्रीय विषयवस्तु नेपालको संविधान (प्रस्तावना) बाट प्रेरणा लिन्छ: राज्यको सामन्तवादी, निरंकुश, केन्द्रीकृत, एकात्मक शासन प्रणालीबाट उत्पन्न सबै प्रकारका भेदभाव र उत्पीडनको उन्मूलन गर्न।",
    },
    {
        "title": "NAPI", "type": "Strategy Project",
        "description": "NAPI lies at the intersectionality of skill education, technology and local solutions. With the tagline, “Measure. Learn. Share” NAPI hopes to foster innovation through various skills based programs and research deliverables. NAPI is named for the rabbits that live in our office.",
        "title_np": "नापी", "type_np": "रणनीतिक नवपर्वतन परियोजना",
        "description_np": "नापी सीप शिक्षा, प्रविधि र स्थानीय समाधानहरूको अन्तरसम्बन्धमा अवस्थित छ। “मापन । सिक्ने । साझा” भन्ने ट्यागलाइनको साथ नापीले विभिन्न सीपमा आधारित कार्यक्रमहरू र वितरण योग्य अनुसन्धानहरू मार्फत नवप्रवर्तनलाई बढावा दिने लक्ष्य राख्छ। “नापी” हाम्रो कार्यालयमा बस्ने खरायोहरूको नामबाट राखिएको हो।",
    },
    {
        "title": "Y5", "type": "Development Initiatives",
        "description": "The Y5 strategic initiatives are a compendium of deliverables emerging from the essence of work here at PRC. Those deliverables includes company programs like our annual fundraiser to team activities like growing lotus plants at the workplace.",
        "title_np": "Y5", "type_np": "विकासका पहलहरू",
        "description_np": "Y5 पहलहरू, पोखरा रिसर्च सेन्टरको कार्यप्रवाहबाट विकसित उपलब्धिहरूको संक्षिप्त संकलन हुन्। ती उपलब्धिहरूमा वार्षिक कोष सङ्कलन कार्यक्रमजस्ता संस्थागत पहलहरूदेखि कार्यस्थलमा कमलका बिरुवा रोप्ने जस्ता अभ्यासहरूसम्म समावेश छन्।",
    },
]

FUNDING_GENERAL = [
    ("Individual & Institutional Donations", "व्यक्तिगत तथा संस्थागत दान"),
    ("Matching Grants", "म्याचिङ ग्रान्ट (पूरक अनुदान)"),
    ("Company Funds", "कम्पनी कोष"),
]

FUNDING_PROJECT = [
    ("Government Grants", "सरकारी अनुदान"),
    ("Single Project Grants (3-9 months)", "एकल परियोजना अनुदान (३–९ महिना)"),
    ("Multi Year Project Grants (3-5 years)", "बहुवर्षीय परियोजना अनुदान (३–५ वर्ष)"),
    ("Innovation Fund / Awards", "नवप्रवर्तन कोष / पुरस्कार"),
]

PROVINCE_CURRENT_PROJECTS = [
    {
        "code": "PRN", "name": "Province ROP Nepal",
        "status": "Ongoing", "status_class": "ongoing",
        "detail": "Published on Play Store; updating new features.",
    },
    {
        "code": "PAT", "name": "Province Assembly Traineeship Program",
        "status": "Completed", "status_class": "completed",
        "detail": "4 Hon. MPAs of Gandaki Province Assembly & trainees selected for pilot program.",
        "link": "https://www.pokharacentre.org/_files/ugd/292b7b_1597a48145004ad69e7e14add808f299.pdf",
        "link_label": "View Details",
    },
    {
        "code": "PIPE", "name": "Province Information Portal & Engagement Tool",
        "status": "Planned", "status_class": "planned",
        "detail": "",
    },
    {
        "code": "PIN", "name": "The Province in Nepal",
        "status": "Planned", "status_class": "planned",
        "detail": "",
    },
    {
        "code": "SGI", "name": "Strengthening Governance Initiatives",
        "status": "Planned", "status_class": "planned",
        "detail": "PMC, Business Promotion Centre : 2026",
    },
]

YPG_BATCHES = [
    ("2020/21", "Gandaki", "गण्डकी", "3 Male, 9 Female", "1:3"),
    ("2021/22", "Karnali", "कर्णाली", "6 Male, 6 Female", "1:1"),
    ("2021/22", "Gandaki", "गण्डकी", "6 Male, 6 Female", "1:1"),
    ("2022/23", "Gandaki", "गण्डकी", "4 Male, 8 Female", "1:2"),
    ("2022/23", "Koshi", "कोशी", "6 Male, 6 Female", "1:1"),
    ("2023/24", "Gandaki", "गण्डकी", "6 Male, 6 Female", "1:1"),
    ("2023/24", "Madhesh", "मधेश", "6 Male, 6 Female", "1:1"),
]

# Past Projects timeline: the PRC project record by donor (2020–2024) plus the
# curated recent projects, newest first. See project_record_data.py.
PAST_PROJECTS = PROJECT_RECORD

FLAGSHIP_PROGRAMS = [
    {
        "title_en": "Youth In Policy & Governance (YPG) Fellowship Program",
        "title_np": "नीति तथा सुशासनमा युवा (वाईपीजी) फेलोसिप कार्यक्रम",
        "description_en": "Our flagship fellowship that equips young Nepali leaders with the skills, exposure, and mentoring to engage with provincial policy. Across multiple cohorts, fellows gain hands-on research experience, take part in youth assemblies, and work directly with lawmakers — building a pipeline of informed, capable leaders for stronger provincial governance.",
        "description_np": "हाम्रो प्रमुख फेलोसिप कार्यक्रम, जसले युवा नेपाली नेतृत्वकर्ताहरूलाई प्रदेश नीतिमा सहभागी हुनका लागि सीप, अभ्यास र मार्गदर्शन प्रदान गर्दछ। विभिन्न समूहहरूमा फेलोहरूले व्यावहारिक अनुसन्धान अनुभव प्राप्त गर्छन्, युवा सभाहरूमा भाग लिन्छन् र प्रत्यक्ष रूपमा विधायकहरूसँग काम गर्छन् — सुदृढ प्रादेशिक सुशासनका लागि जानकार र सक्षम नेतृत्वकर्ताहरूको शृङ्खला निर्माण गर्दै।",
        "image": "website/images/YPG fellows picture/YPG Logo.png",
        "link": "ypg_fellowship", "link_label_en": "Explore", "link_label_np": "थप हेर्नुहोस्",
    },
    {
        "title_en": "Capacity Building Program for Women MPA's and Marginalized MPA's",
        "title_np": "महिला तथा अल्पसङ्ख्यक सांसदहरूको क्षमता अभिवृद्धि कार्यक्रम",
        "description_en": "A dedicated program that strengthens the leadership, legislative skills, and confidence of women and marginalized Members of Provincial Assembly — enabling inclusive representation and more equitable policy-making in Gandaki Province.",
        "description_np": "महिला तथा अल्पसङ्ख्यक प्रदेश सभा सदस्यहरूको नेतृत्व, विधायी सीप र आत्मविश्वास अभिवृद्धि गर्ने विशेष कार्यक्रम — गण्डकी प्रदेशमा समावेशी प्रतिनिधित्व र अधिक न्यायपूर्ण नीति निर्माण सक्षम बनाउँछ।",
        "image": "website/images/pages/province/province-02.jpg",
        "link": "capacity_building", "link_label_en": "Explore", "link_label_np": "थप हेर्नुहोस्",
    },
]

CONSTITUTION_PROJECTS = [
    {
        "name": "3D Exhibition",
        "description": "Virtual exhibition replicating the physical exhibition of CON@11 held at PRC premises from Ashoj 1 - Ashoj 4, 2083",
        "type": "Product",
        "name_np": "थ्रीडी प्रदर्शनी",
        "description_np": "पोखरा रिसर्च सेन्टर परिसरमा असोज १ – असोज ४, २०८३ मा आयोजित CON@11 को भौतिक प्रदर्शनीलाई भर्चुअल रूपमा प्रतिलिपि गरिएको प्रदर्शनी",
        "type_np": "उत्पादन",
    },
]

GALLERY_PHOTOS = [f"website/images/gallery/g{i}.jpg" for i in range(1, 14)]
CONSTITUTION_PHOTOS = [f"website/images/constitution/c{i}.jpg" for i in range(1, 10)]

# Optimized web copies of the new cell photos (generated from the original folders in
# website/static/website/images/{Province photos,Consitituion photos,Institution photos})
PROVINCE_PHOTOS = [f"website/images/pages/province/province-{i:02d}.jpg" for i in range(1, 12)]
CONSTITUTION_RECENT_PHOTOS = [f"website/images/pages/constitution/constitution-{i:02d}.jpg" for i in range(1, 8)]
INSTITUTION_PHOTOS = [f"website/images/pages/institution/institution-{i:02d}.jpg" for i in range(1, 9)]
HOME_PHOTOS = [f"website/images/pages/home/home-{i:02d}.jpg" for i in range(1, 6)]

# YPG Fellowship: optimized copies of the fellows' group photos (per cohort) and fellow testimonials,
# generated from the original folders in website/static/website/images/{YPG fellows picture,testomonials of YPG}
YPG_FELLOWS = [
    {"image": f"website/images/pages/ypg/fellows-{n:02d}.jpg", "cohort_en": en, "cohort_np": np}
    for n, en, np in [
        (1, "Gandaki 2020-21", "गण्डकी २०२०-२१"),
        (2, "Gandaki 2020-21", "गण्डकी २०२०-२१"),
        (3, "Gandaki 2020-21", "गण्डकी २०२०-२१"),
        (4, "Gandaki 2021-22", "गण्डकी २०२१-२२"),
        (5, "Gandaki 2021-22", "गण्डकी २०२१-२२"),
        (6, "Gandaki 2021-22", "गण्डकी २०२१-२२"),
        (7, "Gandaki 2022-23", "गण्डकी २०२२-२३"),
        (8, "Gandaki 2022-23", "गण्डकी २०२२-२३"),
        (9, "Gandaki 2022-23", "गण्डकी २०२२-२३"),
        (10, "Gandaki 2022-23", "गण्डकी २०२२-२३"),
        (11, "Gandaki 2023-24", "गण्डकी २०२३-२४"),
        (12, "Karnali 2021-22", "कर्णाली २०२१-२२"),
        (13, "Koshi 2022-23", "कोशी २०२२-२३"),
        (14, "Koshi 2022-23", "कोशी २०२२-२३"),
        (15, "Koshi 2022-23", "कोशी २०२२-२३"),
        (16, "Madhesh 2023-24", "मधेश २०२३-२४"),
        (17, "YPG Fellows", "वाईपीजी फेलो"),
        (18, "YPG Fellows", "वाईपीजी फेलो"),
        (19, "YPG Fellows", "वाईपीजी फेलो"),
    ]
]
YPG_ALL_FELLOWS = YPG_FELLOWS_DATA
YPG_FEATURED_FELLOWS = YPG_ALL_FELLOWS
YPG_TESTIMONIALS = [f"website/images/pages/ypg/testimonial-{i:02d}.jpg" for i in range(1, 6)]
# Wide group shots for the hero rotation (landscape crops work best behind the title)
YPG_HERO = [f"website/images/pages/ypg/fellows-{i:02d}.jpg" for i in (1, 2, 3, 7, 8, 9, 12, 13, 16, 17, 18)]
EVENT_BANNER_PHOTOS = [f"website/images/events-banner/banner-{i}.jpg" for i in range(1, 5)]

# ------------------------------------------------------------------
# Content is served from the database (editable at /admin/) with the
# constants above as fallback when a table is empty or unavailable.
# ------------------------------------------------------------------
def _qs_or(model, fallback):
    """Visible rows for a section, or the built-in fallback when the table is empty.
    Rows marked hidden in the admin are left out, so an empty result means every
    row is hidden and the section should render empty rather than fall back."""
    try:
        if not model.objects.exists():
            return fallback
        return list(model.objects.filter(is_hidden=False))
    except Exception:
        return fallback

def _urls(refs):
    """Turn static refs into ready-to-use URLs (media uploads already carry .url)."""
    return [r if str(r).startswith("/") or str(r).startswith("http") else static(r) for r in refs]

def _team_list():
    qs = _qs_or(TeamMember, None)
    if qs is None:
        return [{**m, "photo": static(f"website/images/team/t{i}.jpg")} for i, m in enumerate(TEAM, start=1)]
    return [dict(slug=m.slug, category=m.category, en_name=m.en_name, np_name=m.np_name, role_en=m.role_en, role_np=m.role_np,
                 title_en=m.title_en or m.role_en, title_np=m.title_np or m.role_np,
                 bio_en=m.bio_en, bio_np=m.bio_np,photo=m.photo.url if m.photo else "") for m in qs]


def _team_groups():
    """Team members grouped into Executive / Advisor / Research Fellow sections."""
    team = _team_list()
    groups = []
    for value, label_en, label_np in TEAM_GROUPS:
        members = [m for m in team if m.get("category") == value]
        if members:
            groups.append(dict(value=value, label_en=label_en, label_np=label_np, members=members))
    return groups


def _board_list():
    qs = _qs_or(BoardMember, None)
    if qs is None:
        return [{**m, "photo": ""} for m in BOARD]
    return [dict(en_name=m.en_name, np_name=m.np_name, role_en=m.role_en, role_np=m.role_np,
                 photo=m.photo.url if m.photo else "") for m in qs]


def _partner_list():
    qs = _qs_or(Partner, None)
    if qs is None:
        return [{**p, "logo": static(p["logo"])} if p.get("logo") else p for p in PARTNERS]
    return [dict(en=m.en_name, np=m.np_name, type_en=m.type_en, type_np=m.type_np, since=m.since,
                 logo=m.logo.url if m.logo else "") for m in qs]

def _events_list():
    qs = _qs_or(Event, None)
    if qs is None:
        return [{**e, "image": static(e["image"])} if e.get("image") else e for e in EVENTS]
    out = []
    for e in qs:
        out.append(dict(
            title=e.title, image=e.image.url if e.image else "", type=e.type,
            date=e.display_date, date_iso=e.date_iso.isoformat() if e.date_iso else None,
            day=e.day, month=e.month, year=e.year,
            status="ongoing" if e.is_ongoing else "completed",
            description=e.description, reach=e.reach,
            participants=e.participants, link=e.link,
        ))
    return out

def _flagship_link(ref):
    """Resolve a fallback link: route names via reverse, other values used as-is."""
    if not ref:
        return ""
    if ref.startswith(("/", "http", "#")):
        return ref
    return reverse(ref)


def _flagship_programs():
    """Flagship cards for the Province page: DB rows take precedence, else the built-in two."""
    qs = _qs_or(FlagshipProgram, None)
    if qs is None:
        return [
            {**p, "image": static(p["image"]), "link": _flagship_link(p["link"])}
            for p in FLAGSHIP_PROGRAMS
        ]
    return [
        dict(
            title_en=p.title_en, title_np=p.title_np,
            description_en=p.description_en, description_np=p.description_np,
            image=p.image.url if p.image else "",
            link=p.link, link_label_en=p.link_label_en, link_label_np=p.link_label_np,
        )
        for p in qs
    ]


def _gallery(section, fallback):
    qs = _qs_or(GalleryPhoto, None)
    if qs is None:
        return _urls(fallback)
    return [m.image.url for m in qs if m.section == section]

def _pubs_list():
    qs = _qs_or(Publication, None)
    if qs is None:
        return [{**p, "image": static(p["image"])} if p.get("image") else p for p in PUBLICATIONS]
    # cover is a MEDIA file (ImageField) — must use .url, NOT the static tag;
    # routing it through {% static %} produced /static/media/... URLs that 404.
    return [dict(title=m.title, partner=m.partner, wing=m.wing, year=m.year,
                 image=m.cover.url if m.cover else "", link=m.link) for m in qs]

def _blogs_list(fallback=None):
    qs = _qs_or(BlogPost, None)
    if qs is None:
        return fallback or BLOGS
    months = ["", "January", "February", "March", "April", "May", "June",
              "July", "August", "September", "October", "November", "December"]
    return [dict(date=f"{months[m.date.month]} {m.date.day}, {m.date.year}", iso=m.date.isoformat(),
                 title=m.title, author=m.author, title_np=m.title_np, author_np=m.author_np,
                 date_np=m.date_np) for m in qs]

PUBLICATIONS = [
    {"title": "Uddhyam Clinic", "partner": "PMC", "wing": "IGR: PMC", "year": "2026", "image": "website/images/publications/pub-32.jpg", "link": "https://drive.google.com/file/d/1j__ktibwTkDFXRPWNEBJg81oJEUOAs0_/view?usp=sharing"},
    {"title": "Measuring the Knowledge Economy Contribution A Multi-Modular Proxy Indicator Framework with proposed application to Gandaki Province  Training Academy, Nepal", "partner": "GPTA", "wing": "PG: Gandaki", "year": "2026", "image": "website/images/publications/pub-33.jpg", "link": "https://drive.google.com/file/d/10VTQTwrfNu5f0b901iQyemFuc-U37l-V/view?usp=drive_link"},
    {"title": "Pre-Budget Discussion 2081/82 Agriculture Budget", "partner": "TAF", "wing": "PG:Ministry of Economic Affairs", "year": "2025", "image": "website/images/publications/pub-01.jpg", "link": "https://drive.google.com/file/d/1hHSW5-I22TWc_CPic3WegWSaNkNAzidT/view?usp=share_link"},
    {"title": "Taxation & Compliance Ecosystem for Small & Medium Enterprise Gandaki Province", "partner": "CIPE", "wing": "PG:Ministry of Economic Affairs", "year": "2025", "image": "website/images/publications/pub-02.jpg", "link": "https://drive.google.com/file/d/1h738f9KsG8FcH8cgpF4CzhZnoE5fmYNk/view?usp=share_link"},
    {"title": "Building Bridges- Youth Voices of Koshi's Policy Discourse", "partner": "US Embassy Kathmandu", "wing": "PA:Koshi", "year": "2025", "image": "website/images/publications/pub-03.jpg", "link": "https://drive.google.com/file/d/1xeVmktO4Jqo38sylmjSdEe0KICTYyJ3J/view?usp=share_link"},
    {"title": "Uddhyam Clinic", "partner": "PMC", "wing": "IGR:PMC", "year": "2025", "image": "website/images/publications/pub-04.jpg", "link": "https://drive.google.com/file/d/1Jk5rwZqAC8mPpUepsjK-hmEf8IsoT4ST/view?usp=share_link"},
    {"title": "Gandaki Province Budget Analysis FY-2023/24", "partner": "CIPE", "wing": "PG:Ministry of Economic Affairs", "year": "2025", "image": "website/images/publications/pub-05.jpg", "link": "https://drive.google.com/file/d/1Psqz_QbLiZ5hntHwBePzT6TYRg2ZZs2o/view?usp=share_link"},
    {"title": "गण्डकी प्रदेश दलित अधिकार तथा सशक्तिकरण सम्बन्धमा व्यवस्था गर्न बनेको विधेयक अध्ययन तथा राय प्रतिवेदन", "partner": "UNDP", "wing": "PA:Gandaki", "year": "2025", "image": "website/images/publications/pub-06.jpg", "link": "https://drive.google.com/file/d/1N6xH1X5Aqb72HYFk7UU49SW2AwHywZ1T/view?usp=share_link"},
    {"title": "Navigating Oppurtunities: Future of key tourism sector in gandaki province", "partner": "TAF", "wing": "PG:Ministry of Industry, Tourism, Commerce and Supplies", "year": "2024", "image": "website/images/publications/pub-07.jpg", "link": "https://drive.google.com/file/d/1wjn_DkOmht_OGbydShNSWmIBhyM2MZaH/view?usp=share_link"},
    {"title": "Agriculture and Sub-sector", "partner": "TAF", "wing": "PG:Ministry of Land Management, Agriculture, Cooperatives and Poverty Alleviation", "year": "2024", "image": "website/images/publications/pub-08.jpg", "link": "https://drive.google.com/file/d/1JcXhTnCR34I7BOFTG9eczt3epQZ_OS4B/view?usp=share_link"},
    {"title": "Market system analysis of the mechanization subsidy program in the Gandaki Province ꞉ A case of mini tiller subsidy program in Pokhara Metropolitan City (English)", "partner": "TAF", "wing": "PG:Ministry of Land Management, Agriculture, Cooperatives and Poverty Alleviation", "year": "2024", "image": "website/images/publications/pub-09.jpg", "link": "https://drive.google.com/file/d/1sQLm6Godm5JFFBjLsfNyKcXSEFjllnXV/view?usp=share_link"},
    {"title": "Overseeing Gandaki Province Budget: A Primer", "partner": "CIPE", "wing": "PA:Gandaki", "year": "2023", "image": "website/images/publications/pub-10.jpg", "link": "https://drive.google.com/file/d/1uttaCJ_8WkrSF_6TsdaD-PJK70qIXwX3/view?usp=share_link"},
    {"title": "De-mystifying Agriculture Act of Pokhara Metropolitan City (Nepali)", "partner": "ATLAS", "wing": "IGR:PMC", "year": "2023", "image": "website/images/publications/pub-11.jpg", "link": "https://drive.google.com/file/d/1j_8vJVKtg39uV2l2tASjIq6i8OzSaBET/view?usp=share_link"},
    {"title": "Streamlining Private Firm Registration: A study of Gandaki Province", "partner": "ATLAS NETWORK", "wing": "PG:Ministry of Industry, Tourism, Commerce and Supplies", "year": "2023", "image": "website/images/publications/pub-12.jpg", "link": "https://drive.google.com/file/d/1-rf6CTHuWKMwoAvJPt23ygn75_OeWbMg/view?usp=share_link"},
    {"title": "Gandaki Province Pre-Budget Round Table Discussion Fiscal Year 2023/24", "partner": "Centre for International Private Entreprieses", "wing": "PA:OCMCM", "year": "2023", "image": "website/images/publications/pub-13.jpg", "link": "https://drive.google.com/file/d/1p5Sf7IM8TVpfJsTAMD5Wc7op1wUbv10C/view?usp=share_link"},
    {"title": "De-mystifying Agriculture Act of Pokhara Metropolitan City (English)", "partner": "ATLAS", "wing": "IGR:PMC", "year": "2023", "image": "website/images/publications/pub-14.jpg", "link": "https://drive.google.com/file/d/1l5eZqPhccE8fhSBr6LW21t77WXVqcxNi/view?usp=share_link"},
    {"title": "गण्डकी प्रदेशको वनलाई नियमन र व्यवस्थापन गर्न बनेको विधेयकको अध्ययन तथा राय प्रतिवेदन", "partner": "UNDP", "wing": "PG:Ministry of Forests and Environment", "year": "2023", "image": "website/images/publications/pub-15.jpg", "link": "https://drive.google.com/file/d/1YhZkYEx-PAMVPm_P_rbx4jkWDP2r3xfO/view?usp=share_link"},
    {"title": "Policy Brief on Gandaki Province Tourism Act, 2022 (English)", "partner": "ATLAS", "wing": "PG:Ministry of Industry, Tourism, Commerce and Supplies", "year": "2022", "image": "website/images/publications/pub-16.jpg", "link": "https://drive.google.com/file/d/15TYGziJkGz9Zt3QqFpb3Iw4o5LrUct1B/view?usp=share_link"},
    {"title": "Policy Brief on Province Industrial Enterprise Act, 2019 Gandaki Province (Nepali)", "partner": "CIPE", "wing": "PG:Ministry of Industry, Tourism, Commerce and Supplies", "year": "2022", "image": "website/images/publications/pub-17.jpg", "link": "https://drive.google.com/file/d/1BXwRxZsywCFUNr2kTgGtF-TmZh9vSuIY/view?usp=share_link"},
    {"title": "Policy Brief on Gandaki Province Tourism Act, 2022 (Nepali)", "partner": "ATLAS", "wing": "PG:Ministry of Industry, Tourism, Commerce and Supplies", "year": "2022", "image": "website/images/publications/pub-18.jpg", "link": "https://drive.google.com/file/d/1bVknhcaBGc4OpXrfmWoJeuvil7AhRl05/view?usp=share_link"},
    {"title": "Market system analysis of the mechanization subsidy program in the Gandaki Province ꞉ A case of mini tiller subsidy program in Pokhara Metropolitan City (Nepali)", "partner": "TAF", "wing": "PG:Ministry of Land Management, Agriculture, Cooperatives and Poverty Alleviation", "year": "2024", "image": "website/images/publications/pub-19.jpg", "link": "https://drive.google.com/file/d/1uVp3khXG4-btT0DQ1LDZ-Ip9KV7fzFRK/view?usp=share_link"},
    {"title": "MCSIs in Gandaki Province: The Province-Level Policy Instruments and Challenges Facing Them", "partner": "CIPE", "wing": "PG:Ministry of Industry, Tourism, Commerce and Supplies", "year": "2024", "image": "website/images/publications/pub-20.jpg", "link": "https://drive.google.com/file/d/1BXDrp2JyV-NCqa2XsLsVqXbGS7c0tYnA/view?usp=share_link"},
    {"title": "Industry Sector in Gandaki Province", "partner": "TAF", "wing": "PG:Ministry of Industry, Tourism, Commerce and Supplies", "year": "2024", "image": "website/images/publications/pub-21.jpg", "link": "https://drive.google.com/file/d/1y3tHpW-L1aRQt_lD72Seesw0KVj7lexD/view?usp=share_link"},
    {"title": "Mid-Term Budget Review: Fiscal Year 2080/81", "partner": "CIPE", "wing": "PG:Ministry of Economic Affairs", "year": "2024", "image": "website/images/publications/pub-22.jpg", "link": "https://drive.google.com/file/d/13eMcXHQv-eKa743fTDYDDDG1J81WyACN/view?usp=share_link"},
    {"title": "Gandaki Province Budget Summary FY-2024/25", "partner": "CIPE", "wing": "PG:Ministry of Economic Affairs", "year": "2024", "image": "website/images/publications/pub-23.jpg", "link": "https://drive.google.com/file/d/1R-io0es583_qOfnfPKUWgT4t1dsAmatR/view?usp=share_link"},
    {"title": "Provincial Assembly Procedures A Primer", "partner": "Institutional", "wing": "PA:Gandaki", "year": "2023", "image": "website/images/publications/pub-24.jpg", "link": "https://drive.google.com/file/d/1lGHM7s80DO9gnNntNihMSdCQdIJvb7LM/view?usp=share_link"},
    {"title": "Budget Analysis of Gandaki Province", "partner": "CIPE", "wing": "PG:Ministry of Economic Affairs", "year": "2023", "image": "website/images/publications/pub-25.jpg", "link": "https://drive.google.com/file/d/13537Z6Ir2cLgGVCaUj6U8wdbk9cFEEHP/view?usp=share_link"},
    {"title": "Agribusiness Promotion Act of PMC", "partner": "ATLAS", "wing": "IGR:PMC", "year": "2023", "image": "website/images/publications/pub-26.jpg", "link": "https://drive.google.com/file/d/1jFzoiE459u1Wcq35A9saVsCLMMgefxPV/view?usp=share_link"},
    {"title": "The Koshi Province Primer", "partner": "Institutional", "wing": "PA:Koshi", "year": "2023", "image": "website/images/publications/pub-27.jpg", "link": "https://drive.google.com/file/d/1pzqprTbcyNK-9bfJZ8xFskhvlDxpM717/view?usp=share_link"},
    {"title": "Analyzing Motor Vehicle Tax in Gandaki Province", "partner": "CIPE", "wing": "PG:Ministry of Physical Infrastructure and Transport Management", "year": "2023", "image": "website/images/publications/pub-28.jpg", "link": "https://drive.google.com/file/d/1Qk6usnO7d22X0fpF0Z_cw45kvNivbXQ_/view?usp=share_link"},
    {"title": "Policy Brief on Province Industrial Enterprise Act, 2019 Gandaki Province (English)", "partner": "CIPE", "wing": "PG:Ministry of Industry, Tourism, Commerce and Supplies", "year": "2022", "image": "website/images/publications/pub-29.jpg", "link": "https://drive.google.com/file/d/1wfv3sf32WjcwRwZsZrI4CfvyNcdH6Am_/view?usp=share_link"},
    {"title": "Pokhara Metropolitan City’s Smart City Initiatives : Turning Ambitions Into Reality Pokhara", "partner": "ATLAS NETWORK", "wing": "IGR:PMC", "year": "2021", "image": "website/images/publications/pub-30.jpg", "link": "https://drive.google.com/file/d/1pLf943zJqj732Ugw9flZkeqcQ_hXwbwZ/view?usp=drive_link"},
    {"title": "Strategic Approach To Solve Parking Problem In Pokhara", "partner": "ATLAS NETWORK", "wing": "IGR:PMC", "year": "2021", "image": "website/images/publications/pub-31.jpg", "link": "https://drive.google.com/file/d/1z0FKsHTJEPdh7HVY5SwcWmtq7EVe_kNC/view?usp=share_link"},]


def home(request):
    return render(request, "website/home.html", {
        "gallery_photos": _gallery(GalleryPhoto.Section.HOME_GALLERY, GALLERY_PHOTOS),
        "home_photos": _gallery(GalleryPhoto.Section.HERO_HOME, HOME_PHOTOS),
        "stats": {
            # Headline impact metrics for the home page metrics strip
            "female_mpas": 120,
            "youth_trained": 350,
            "fellows_trained": YPGFellowProfile.objects.filter(is_hidden=False).count() or len(YPG_ALL_FELLOWS),
            "legislative_discussions": 80,
        },
    })


def institution(request):
    team_with_photos = _team_list()
    # Show most recent partnerships first
    partners_list = _partner_list()
    partners_sorted = sorted(
        partners_list,
        key=lambda p: int(re.search(r"\d{4}", p["since"]).group()),
        reverse=True,
    )
    return render(request, "website/institution.html", {
        "board_members": _board_list(),
        "team": team_with_photos,
        "team_groups": _team_groups(),
        "partners": partners_sorted,
        "projects": _qs_or(InstitutionProject, INSTITUTION_PROJECTS),
        "funding_general": [(i.en, i.np) for i in FundingItem.objects.filter(category=FundingItem.Category.GENERAL, is_hidden=False)] or FUNDING_GENERAL,
        "funding_project": [(i.en, i.np) for i in FundingItem.objects.filter(category=FundingItem.Category.PROJECT, is_hidden=False)] or FUNDING_PROJECT,
        "cell_photos": _gallery(GalleryPhoto.Section.HERO_INSTITUTION, INSTITUTION_PHOTOS),  # used by hero slides
    })


def province(request):
    return render(request, "website/province.html", {
        "ypg_batches": [(b.year, b.province_en, b.province_np, b.participation, b.ratio) for b in YPGBatch.objects.filter(is_hidden=False)] or YPG_BATCHES,
        "flagship_programs": _flagship_programs(),
        "past_projects": _qs_or(PastProject, PAST_PROJECTS),
        "province_photos": _gallery(GalleryPhoto.Section.HERO_PROVINCE, PROVINCE_PHOTOS),
        "current_projects": _qs_or(ProvinceProject, PROVINCE_CURRENT_PROJECTS),
    })


def capacity_building(request):
    return render(request, "website/capacity_building.html", {
        "province_photos": _gallery(GalleryPhoto.Section.HERO_PROVINCE, PROVINCE_PHOTOS),
    })


def ypg_fellowship(request):
    fellows = YPGFellow.objects.filter(is_hidden=False)
    testimonials = YPGTestimonial.objects.filter(is_hidden=False)
    fellowship_photos = ([dict(image=f.image.url, cohort_en=f.cohort_en, cohort_np=f.cohort_np) for f in fellows]
                         if YPGFellow.objects.exists()
                         else [{**f, "image": static(f["image"])} for f in YPG_FELLOWS])

    # Fellows wall: DB-managed profiles take precedence; fall back to the hardcoded list
    db_profiles = YPGFellowProfile.objects.filter(is_hidden=False)
    if db_profiles.exists():
        all_fellows = [
            {
                "id": p.slug,
                "image": p.image.url,
                "name_en": p.name_en,
                "name_np": p.name_np,
                "year_en": p.year_en,
                "year_np": p.year_np,
                "province_en": p.province_en,
                "province_np": p.province_np,
                "cohort_en": p.cohort_en,
                "cohort_np": p.cohort_np,
                "education_en": p.education_en,
                "education_np": p.education_np,
                "post_grad_en": p.post_grad_en,
                "post_grad_np": p.post_grad_np,
                "address_en": getattr(p, "address_en", ""),
                "address_np": getattr(p, "address_np", ""),
                "current_engagement": getattr(p, "current_engagement", ""),
                "bio_en": p.bio_en,
                "bio_np": p.bio_np,
            }
            for p in db_profiles
        ]
    else:
        # Resolve static URLs for all fellows
        all_fellows = [{**f, "image": static(f["image"])} for f in YPG_ALL_FELLOWS]

    photo_years = {}
    additional_photos = []

    for photo in fellowship_photos:
        match = re.search(r"(\d{4})[-/](\d{2})$", photo["cohort_en"])
        if match:
            year = f"{match.group(1)}-{match.group(2)}"
            year_group = photo_years.setdefault(year, {
                "year_en": year,
                "year_np": photo["cohort_np"].rsplit(" ", 1)[-1].replace("-", "/"),
                "photos": [],
            })
            year_group["photos"].append(photo)
        else:
            additional_photos.append(photo)

    fellow_years_map = {}
    for fellow in all_fellows:
        year = fellow["year_en"]
        if year not in fellow_years_map:
            fellow_years_map[year] = {
                "year_en": year,
                "year_np": fellow["year_np"],
                "fellows": [],
                "provinces": set(),
            }
        fellow_years_map[year]["fellows"].append(fellow)
        fellow_years_map[year]["provinces"].add(fellow["province_en"])

    sorted_fellow_years = []
    for year in sorted(fellow_years_map.keys(), reverse=True):
        group = fellow_years_map[year]
        group["provinces"] = sorted(list(group["provinces"]))
        group["portraits"] = group["fellows"]  # backward compatibility
        sorted_fellow_years.append(group)

    return render(request, "website/ypg_fellowship.html", {
        "ypg_batches": [(b.year, b.province_en, b.province_np, b.participation, b.ratio) for b in YPGBatch.objects.filter(is_hidden=False)] or YPG_BATCHES,
        "ypg_fellowship_years": sorted_fellow_years,
        "ypg_all_fellows": all_fellows,
        "ypg_all_fellows_json": json.dumps(all_fellows),
        "ypg_fellowship_photo_years": [photo_years[year] for year in sorted(photo_years, reverse=True)],
        "ypg_fellowship_additional_photos": additional_photos,
        "ypg_testimonials": ([t.image.url for t in testimonials] if YPGTestimonial.objects.exists()
                             else _urls(YPG_TESTIMONIALS)),
        "ypg_hero": _gallery(GalleryPhoto.Section.HERO_YPG, YPG_HERO),
    })


def constitution(request):
    return render(request, "website/constitution.html", {
        "constitution_photos": _gallery(GalleryPhoto.Section.CONSTITUTION_GALLERY, CONSTITUTION_PHOTOS),
        "constitution_recent": _gallery(GalleryPhoto.Section.HERO_CONSTITUTION, CONSTITUTION_RECENT_PHOTOS),
    })


BLOGS = [
    {"date": "August 20, 2026", "iso": "2026-08-20", "title": "Reflecting on The Borrowed Futures of Nepal's Foreign Policy", "author": "Research Team",
     "title_np": "नेपालको परराष्ट्र नीतिको उधारो भविष्यबारे चिन्तन", "author_np": "अनुसन्धान टिम", "date_np": "अगस्ट २०, २०२६"},
    {"date": "December 15, 2025", "iso": "2025-12-15", "title": "From AIT to Global Impact: A Journey in Gender and Climate Leadership", "author": "Office of Communications",
     "title_np": "एआईटीदेखि विश्वस्तरीय प्रभावसम्म: लैङ्गिकता र जलवायु नेतृत्वको यात्रा", "author_np": "सञ्चार महाशाखा", "date_np": "डिसेम्बर १५, २०२५"},
    {"date": "October 29, 2025", "iso": "2025-10-29", "title": "Climate change: What Nepal's local leaders think about it", "author": "Research Associate",
     "title_np": "जलवायु परिवर्तन: नेपालका स्थानीय नेतृत्वकर्ताहरू के सोच्छन्?", "author_np": "अनुसन्धान सहायक", "date_np": "अक्टोबर २९, २०२५"},
    {"date": "August 4, 2025", "iso": "2025-08-04", "title": "On the Evolution of Nepali Civil Society: Co-Opted or Still Catalyzing Change?", "author": "Researcher",
     "title_np": "नेपाली नागरिक समाजको विकासक्रम: उपयोग भयो वा अझै परिवर्तनका कटुस?", "author_np": "अनुसन्धानकर्ता", "date_np": "अगस्ट ४, २०२५"},
    {"date": "April 29, 2024", "iso": "2024-04-29", "title": "Evidence-Based Policy Making in Nepal: Challenges and the Way Forward", "author": "Program Coordinator",
     "title_np": "नेपालमा प्रमाण–आधारित नीति निर्माण: चुनौती र अगाडिको बाटो", "author_np": "कार्यक्रम संयोजक", "date_np": "अप्रिल २९, २०२४"},
]


def archives(request):
    blogs = BLOGS
    return render(request, "website/archives.html", {"blogs": _blogs_list(blogs)})


def support_us(request):
    return render(request, "website/support_us.html")


def publications(request):
    pubs = sorted(_pubs_list(), key=lambda p: (p["year"], p["title"]), reverse=True)
    years = sorted({p["year"] for p in PUBLICATIONS}, reverse=True)
    partners = sorted({p["partner"] for p in PUBLICATIONS})
    wings = sorted({p["wing"] for p in PUBLICATIONS})
    return render(request, "website/publications.html", {
        "publications": pubs,
        "years": years,
        "partners": partners,
        "wings": wings,
    })


def team_member(request, slug):
    team = _team_list()
    by_slug = {m["slug"]: m for m in team}
    member = by_slug.get(slug)
    if member is None:
        raise Http404("Team member not found")
    index = next(i for i, m in enumerate(team, start=1) if m["slug"] == slug)
    prev_index = index - 2  # 0-based position of previous member
    next_index = index      # 0-based position of next member
    context = {
        "member": member,
        "photo": member.get("photo") or f"website/images/team/t{index}.jpg",
        "prev_member": team[prev_index] if prev_index >= 0 else None,
        "next_member": team[next_index] if next_index < len(team) else None,
    }
    return render(request, "website/team_member.html", context)


EVENTS = [
    {
        "title": "Training of Trainers (ToT) organized by CODE",
        "image": "website/images/events/sync-21.jpg",
        "date": "3-5 Nov, 2026",
        "date_iso": "2026-11-03",
        "day": "3-5",
        "month": "Nov",
        "year": "2026",
        "type": "Workshop",
        "status": "completed",
        "description": "Representing Pokhara Research Center, our team members participated in the Training of Trainers (ToT) Workshop under the Creating Opportunities for Youth in the Digital Economy (CODE) Project, held in Chitwan from 3–5 November 2026. Building knowledge, strengthening skills, and empowering communities through digital literacy!. The three-day workshop provided an opportunity to deepen their understanding of the Digital Literacy Handbook, strengthen practical training and facilitation skills, and enhance their knowledge of project reporting, financial management, and compliance procedures",
        "reach": "PRC, Restless Development, Swisscontact, the Robotics Association of Nepal, and the European Union",
        "participants": ""
    },
    {
        "title": "SAMVAD: Reducing Youth Migration through Free Markets",
        "image": "website/images/events/sync-22.jpg",
        "date": "03 Nov, 2026",
        "date_iso": "2026-11-03",
        "day": "03",
        "month": "Nov",
        "year": "2026",
        "type": "Programme",
        "status": "completed",
        "description": "Pokhara Research Centre hosted the SAMVAD program, organized by Students For Liberty South Asia, on November 3, 2026. The event focused on the theme \"Reducing Youth Migration through Free Markets\" and aimed to make staying in Nepal a genuine choice of opportunity. The session recorded 22 participants from various academic institutions, including Nepal Law Campus, Institute of Forestry, Gandaki University, Prithvi Narayan Campus, Pokhara University, Paschimanchal Campus, and Kathmandu University.",
        "reach": "PRC, Youth leaders, Students",
        "participants": "22 participants"
    },
    {
        "title": "The Cost of Politics",
        "image": "website/images/events/sync-19.jpg",
        "date": "01 Oct, 2026",
        "date_iso": "2026-10-01",
        "day": "01",
        "month": "Oct",
        "year": "2026",
        "type": "Programme",
        "status": "completed",
        "description": "The Pokhara Research Centre (PRC), with the support of the Westminster Foundation for Democracy (WFD), organised a discussion on “The Cost of Politics,” drawing on findings from WFD’s research on the financial costs of political participation in Nepal at Hotel Batika, Pokhara. The session featured a presentation by Mr. Dinesh Wagle, followed by reflections from Dr. Deepak Prakash Bhatt, former Member of Parliament, House of Representatives. Participants actively engaged in the discussion, sharing perspectives on the financial barriers to political participation, inclusive representation, and Nepal’s political and electoral processes.",
        "reach": "WFD, Youth leaders, Political parties representative, Media (Samadhan and Yatrasamachar), PMC - Youth Council",
        "participants": "23 participants"
    },
    {
        "title": "Developers Community Meetup Pokhara",
        "image": "website/images/events/sync-20.jpg",
        "date": "22 Aug, 2026",
        "date_iso": "2026-08-22",
        "day": "22",
        "month": "Aug",
        "year": "2026",
        "type": "Programme",
        "status": "completed",
        "description": "Facilitated interactive program at PRC where Developers Community Pokhara, had an insightful and interactive session with Bikram Adhikari, Founder of Nētly.AI & The Reading Revellers. Discussion around: Why should developers read? What & how should we read? What can we build from what we read?",
        "reach": "Tech companies, Tech leaders, Students, Tech Expert",
        "participants": "17 participants"
    },
    {
        "title": "Pokhara Dialogue Series V1S2: Strengthening Think Tanks and Provincial Governance",
        "image": "website/images/events/sync-18.jpg",
        "date": "20 Aug, 2026",
        "date_iso": "2026-08-20",
        "day": "20",
        "month": "Aug",
        "year": "2026",
        "type": "Dialogue",
        "status": "completed",
        "description": "Dr. Kuldeep Niraula, a researcher and Fulbright scholar with experience in US government, NGO and think tank work, discussed how think tanks can build stakeholder relationships, choose research priorities and communicate with the public through simple, engaging narratives. The conversation also covered how to shift public perception of provincial government and what it will take to put constitutionally guaranteed provincial powers into practice",
        "reach": "",
        "participants": "11 participants"
    },
    {
        "title": "Pokhara Dialogue Series V1S1: Technology, Talent and Research in Nepal",
        "image": "website/images/events/sync-17.jpg",
        "date": "17 Aug, 2026",
        "date_iso": "2026-08-17",
        "day": "17",
        "month": "Aug",
        "year": "2026",
        "type": "Dialogue",
        "status": "completed",
        "description": "Er. Bikram Adhikari, an engineer and AI professional based in Silicon Valley, joined PRC for a conversation on brain drain, the gap between academia and the job market, and how AI is changing work. The PRC team also sought his feedback on the Province Information and Engagement Portal (PIPE), including its research design and a realistic six-month scope. The session ended with a proposal for a Pokhara Reading Group to encourage critical thinking and discussion",
        "reach": "",
        "participants": "11 participants"
    },
    {
        "title": "Multi-Stakeholder Dialogue on Digital Entrepreneurship, Remote Work Ecosystem, and IT Infrastructure Development in Gandaki Province",
        "image": "website/images/events/sync-5.jpg",
        "date": "12 Aug, 2026",
        "date_iso": "2026-08-12",
        "day": "12",
        "month": "Aug",
        "year": "2026",
        "type": "Dialogue",
        "status": "completed",
        "description": "Co-organized by NYEF and PRC, this NOIS-framework dialogue examined barriers to Gandaki's digital economy and the stalled Pokhara IT Park, drawing government, industry, and academic input toward a forthcoming policy advocacy report.",
        "reach": "PRC, NYEF Pokhara Chapter, UNDP, Government of Gandaki Province, Pokhara Metropolitan City, Nepal Rastra Bank, FNCCI, GTEVT, IT companies, academia, media (112 participants)",
        "participants": "112 participants"
    },
    {
        "title": "Presentation Program on the Uddhyam Clinic Consolidated Report – 2083",
        "image": "website/images/events/sync-1.jpg",
        "date": "13 Jul, 2026",
        "date_iso": "2026-07-13",
        "day": "13",
        "month": "Jul",
        "year": "2026",
        "type": "Report Launch",
        "status": "completed",
        "description": "Co-organized by BPC and PRC, this presentation released a field-based study of SME sustainability and competitiveness across Pokhara, featuring a business-friendliness index framework and generating multi-stakeholder discussion on taxation, registration, and rent-regulation reform, with policy commitments from Pokhara Metropolitan City.",
        "reach": "Business Promotion Center, PMC Economic Development Department, PRC, Lekhnath & Pokhara Chambers of Commerce, NYEF Pokhara Chapter, SME/business owners across tourism, hospitality, agriculture, manufacturing, construction",
        "participants": ""
    },
    {
        "title": "Expert Consultation and Feedback Session on Knowledge-Based Transformation & Knowledge Economy",
        "image": "website/images/events/sync-13.jpg",
        "date": "02 Jul, 2026",
        "date_iso": "2026-07-02",
        "day": "02",
        "month": "Jul",
        "year": "2026",
        "type": "Consultation",
        "status": "completed",
        "description": "Co-organized by PRC and GPTA, this consultation presented PRC's Knowledge Economy paper to government officials and academics, gathering feedback on the framework's feasibility ahead of finalization.",
        "reach": "PRC, GPTA, Government of Gandaki Province officials, academicians, policy experts (30 participants)",
        "participants": "30 participants"
    },
    {
        "title": "FCDO Regional Workshop : Understanding Youth Mobilization Around September 2025 Events and Its Implications for Political Change in Nepal",
        "image": "website/images/events/sync-7.jpg",
        "date": "23 Jun, 2026",
        "date_iso": "2026-06-23",
        "day": "23",
        "month": "Jun",
        "year": "2026",
        "type": "Workshop",
        "status": "completed",
        "description": "Commissioned by FCDO through PEI, with PRC as local logistics partner, this workshop examined why Gen Z-led mobilizations bypassed traditional intermediary structures through structured small-group discussions on institutional unaccountability and post-movement political dynamics.",
        "reach": "PEI, FCDO, PRC, Pokhara Chamber of Commerce and Industry, regional civil society, youth/Gen Z civic actors (22 participants)",
        "participants": "22 participants"
    },
    {
        "title": "Statistical Analysis of Province Assembly Events (PAE): A Dataset Approach - Stakeholder Consultation",
        "image": "website/images/events/sync-11.jpg",
        "date": "01 Jun, 2026",
        "date_iso": "2026-06-01",
        "day": "01",
        "month": "Jun",
        "year": "2026",
        "type": "Consultation",
        "status": "completed",
        "description": "A closed-door roundtable bridging legislative data and academic interpretation, showcasing the PAE Dataset's methodology to postgraduate Economics students, with discussion on the dataset's governance implications and PRC's role as Gandaki's provincial think tank.",
        "reach": "PRC, Prithvi Narayan Campus (Tribhuvan University), postgraduate MBS/MA Economics students, Gandaki Province Assembly",
        "participants": ""
    },
    {
        "title": "Province Assembly Traineeship (PAT) : Capacity Building Programme for Gandaki Provincial Assembly",
        "image": "website/images/events/sync-16.jpg",
        "date": "16 Mar, 2026",
        "date_iso": "2026-03-16",
        "day": "16",
        "month": "Mar",
        "year": "2026",
        "type": "Capacity Building",
        "status": "completed",
        "description": "A capacity-building programme placed four trained youth research assistants with MPAs to strengthen accountability questioning, bill drafting, and evidence-based debate, marking the first time Assembly questions were prepared with dedicated research support.",
        "reach": "Gandaki Province Assembly, PRC Province Cell, youth trainees/research assistants",
        "participants": ""
    },
    {
        "title": "International Women's Day Celebration - Women in Leadership & Entrepreneurship",
        "image": "website/images/events/sync-6.jpg",
        "date": "08 Mar, 2026",
        "date_iso": "2026-03-08",
        "day": "08",
        "month": "Mar",
        "year": "2026",
        "type": "Celebration",
        "status": "completed",
        "description": "An interactive session at PRC's Fishtail Rooftop featuring women sharing their journeys through moderated experience-sharing, Q&A, and networking, celebrating women's leadership and resilience.",
        "reach": "PRC, women entrepreneurs, KOPILA Nepal, Press Register, Pahilo Paila Nepal, young professionals (24 participants)",
        "participants": "24 participants"
    },
    {
        "title": "Open Door Weekend",
        "image": "website/images/events/sync-23.jpg",
        "date": "14 Jan, 2026",
        "date_iso": "2026-01-14",
        "day": "14",
        "month": "Jan",
        "year": "2026",
        "type": "Programme",
        "status": "completed",
        "description": "A flagship stakeholder engagement event combining static exhibits, dynamic dialogues, and digital outreach across four days: Ward 11 community inauguration, youth-focused sessions (social media debate, PAT orientation, Gen-Z policy dialogue), sector roundtables (trekking guides, tech professionals), and an inter-level women's leadership dialogue.",
        "reach": "PRC, Ward 11 community, youth/Gen-Z civic actors, trekking guides, tech entrepreneurs and IT students, women MPAs and local women leaders",
        "participants": ""
    },
    {
        "title": "Gandaki Agriculture Hackathon",
        "image": "website/images/events/sync-4.jpg",
        "date": "20 Dec, 2025",
        "date_iso": "2025-12-20",
        "day": "20",
        "month": "Dec",
        "year": "2025",
        "type": "Hackathon",
        "status": "completed",
        "description": "A PRC initiative convening students, farmers, and private-sector actors to co-create tech-enabled policy solutions for agricultural commercialization and governance, culminating in a pitch event and post-event mentorship producing policy-ready proposals for the provincial government.",
        "reach": "PRC, The Asia Foundation Nepal, Ministry of Agriculture, Land Management and Cooperatives, five academic partner institutions, students, farmers, agri-business owners",
        "participants": ""
    },
    {
        "title": "CON@10 Exhibition : Nepal's Constitution, A Decade of Democracy",
        "image": "website/images/events/sync-2.jpg",
        "date": "12 Oct, 2025",
        "date_iso": "2025-10-12",
        "day": "12",
        "month": "Oct",
        "year": "2025",
        "type": "Exhibition",
        "status": "completed",
        "description": "A multi-stall interactive exhibition marking the tenth anniversary of Nepal's Constitution, tracing the constitution-making process through historical archives, multilingual displays, and comparative constitutional data across eleven thematic stalls, culminating in a petition for a Law Book Library in the Province Capital.",
        "reach": "PRC, Gandaki Province Assembly, artists, government bureaucrats, province-level institutions, young professionals, tourists (94 participants)",
        "participants": "94 participants"
    }
]

def events(request):
    events_data = _events_list()
    dated = [e for e in events_data if e.get("date_iso")]
    undated = [e for e in events_data if not e.get("date_iso")]
    ordered = sorted(dated, key=lambda e: e["date_iso"], reverse=True) + undated

    # A day/month/year block can't express a range ("12th to 17th October"), a Nepali
    # month ("Ashar 2083 (June/July 2026)") or a live label ("Ongoing · Virtual"), so
    # keep the full text for those and show it as a detail line under the date block.
    # Events with no date on record show a neutral label instead of an invented one.
    _RICH_DATE = (" to ", "\u2013", " - ", "(", "\u00b7")
    for e in events_data:
        full = (e.get("date") or "").strip()
        e["date_detail"] = full if any(m in full for m in _RICH_DATE) else ""
        e["date_unknown"] = not (full or e.get("day") or e.get("month"))

    # Classify for the Upcoming / Happening / Completed tabs (IIDS-style).
    # Status keys must match the tab data-status values in events.html.
    from datetime import date as _date
    today = _date.today()
    for e in ordered:
        if e.get("status") == "ongoing":
            e["status"] = "happening"  # running now
        elif e.get("date_iso"):
            try:
                y, m, d = (int(x) for x in e["date_iso"].split("-"))
                e["status"] = "upcoming" if _date(y, m, d) > today else "completed"
            except ValueError:
                e["status"] = "completed"
        else:
            e["status"] = "completed"

    # Completed first (newest), then undated, then ongoing — the initial tab
    # is whichever category has events (IIDS behaviour), so keep Completed leading.
    ordered = (
        [e for e in ordered if e["status"] == "completed"]
        + [e for e in ordered if e["status"] not in ("completed", "happening")]
        + [e for e in ordered if e["status"] == "happening"]
    )

    years = sorted({e["year"] for e in events_data if e.get("year")}, reverse=True)
    types = sorted({e["type"] for e in events_data})
    return render(request, "website/events.html", {
        "events": ordered,
        "years": years,
        "types": types,
    })