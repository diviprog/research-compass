#!/usr/bin/env python3
"""
Seed the SQLite database with 15 diverse sample research opportunities.
Run from backend directory: python seed_opportunities.py
"""

from datetime import datetime, timedelta
from app.db.database import SessionLocal
from app.models.opportunity import Opportunity


def get_sample_opportunities():
    """Return 15 diverse research opportunities with full schema fields."""
    base_url = "https://example.edu/labs"
    now = datetime.utcnow()

    return [
        {
            "source_url": f"{base_url}/mit-vision-lab",
            "title": "Research Assistant – Computer Vision and Multimodal Learning",
            "description": (
                "We are seeking a motivated research assistant to work on cutting-edge computer vision "
                "and multimodal learning projects. The position involves developing novel deep learning "
                "architectures for image and video understanding, working with large-scale datasets, and "
                "contributing to publication-quality research. Ideal candidates have strong Python skills, "
                "experience with PyTorch or TensorFlow, and a solid foundation in linear algebra and "
                "probability. This role offers close mentorship and opportunities to co-author papers."
            ),
            "lab_name": "Vision Intelligence Lab",
            "pi_name": "Dr. Sarah Chen",
            "institution": "MIT",
            "research_topics": ["Computer Vision", "Deep Learning", "Multimodal Learning", "Video Understanding"],
            "methods": ["Neural Networks", "Transformers", "Self-Supervised Learning", "Contrastive Learning"],
            "datasets": ["ImageNet", "COCO", "Kinetics", "LAION"],
            "deadline": now + timedelta(days=30),
            "funding_status": "funded",
            "experience_required": "undergraduate",
            "contact_email": "visionlab@mit.edu",
            "application_link": f"{base_url}/mit-vision-lab/apply",
            "is_active": True,
            "location_city": "Cambridge",
            "location_state": "MA",
            "is_remote": False,
            "degree_levels": ["undergraduate", "masters"],
            "min_hours": 15,
            "max_hours": 25,
            "paid_type": "stipend",
        },
        {
            "source_url": f"{base_url}/stanford-nlp-phd",
            "title": "PhD Student Opening – Natural Language Processing and Large Language Models",
            "description": (
                "Fully funded PhD position in Natural Language Processing with a focus on large language "
                "models and their applications. Projects include efficient fine-tuning methods, interpretability "
                "of transformer models, and applications in healthcare and education. We offer competitive "
                "stipend, full tuition coverage, and collaboration with leading industry research labs. "
                "Applicants should have a strong background in machine learning, programming, and preferably "
                "prior research or publication experience in NLP or related areas."
            ),
            "lab_name": "Stanford NLP Group",
            "pi_name": "Dr. Michael Zhang",
            "institution": "Stanford University",
            "research_topics": ["NLP", "Large Language Models", "AI Safety", "Efficient ML"],
            "methods": ["Transformers", "Fine-tuning", "Prompt Engineering", "Reinforcement Learning"],
            "datasets": ["C4", "The Pile", "GLUE", "SuperGLUE"],
            "deadline": now + timedelta(days=45),
            "funding_status": "funded",
            "experience_required": "masters",
            "contact_email": "nlp-recruiting@stanford.edu",
            "application_link": f"{base_url}/stanford-nlp-phd/apply",
            "is_active": True,
            "location_city": "Stanford",
            "location_state": "CA",
            "is_remote": False,
            "degree_levels": ["masters", "phd"],
            "min_hours": 40,
            "max_hours": 50,
            "paid_type": "stipend",
        },
        {
            "source_url": f"{base_url}/berkeley-robotics-internship",
            "title": "Summer Research Internship – Robotics and Manipulation",
            "description": (
                "Ten-week summer research internship focused on robotic manipulation using reinforcement "
                "learning and imitation learning. Interns will work on real robotic systems, develop "
                "simulation environments, and contribute to ongoing research projects. This is an excellent "
                "opportunity for undergraduates interested in pursuing graduate studies in robotics or "
                "machine learning. Prior experience with ROS, Python, and basic machine learning is preferred "
                "but not required. Housing stipend and travel support may be available."
            ),
            "lab_name": "Berkeley Robot Learning Lab",
            "pi_name": "Dr. Emma Rodriguez",
            "institution": "UC Berkeley",
            "research_topics": ["Robotics", "Reinforcement Learning", "Manipulation", "Sim-to-Real"],
            "methods": ["RL", "Imitation Learning", "Sim-to-Real Transfer", "Policy Learning"],
            "datasets": ["D4RL", "RoboNet", "Open X-Embodiment"],
            "deadline": now + timedelta(days=60),
            "funding_status": "funded",
            "experience_required": "undergraduate",
            "contact_email": "robotics@berkeley.edu",
            "application_link": None,
            "is_active": True,
            "location_city": "Berkeley",
            "location_state": "CA",
            "is_remote": False,
            "degree_levels": ["undergraduate"],
            "min_hours": 35,
            "max_hours": 40,
            "paid_type": "stipend",
        },
        {
            "source_url": f"{base_url}/cmu-hci-postdoc",
            "title": "Postdoctoral Researcher – Human–Computer Interaction and AI",
            "description": (
                "We seek a postdoctoral researcher to join our lab at the intersection of AI and "
                "human–computer interaction. Research areas include AI-assisted design and creativity tools, "
                "explainable AI interfaces, user studies and evaluation methods, and collaborative human–AI "
                "systems. The position is for two years with possibility of extension. Competitive salary "
                "and benefits are included. Applicants must have a PhD in HCI, CS, or a related field and "
                "strong publication record. Experience with both ML systems and user studies is highly valued."
            ),
            "lab_name": "Human–AI Interaction Lab",
            "pi_name": "Dr. James Williams",
            "institution": "Carnegie Mellon University",
            "research_topics": ["HCI", "AI", "UX Design", "Explainable AI"],
            "methods": ["User Studies", "Prototyping", "A/B Testing", "Qualitative Analysis"],
            "datasets": [],
            "deadline": now + timedelta(days=75),
            "funding_status": "funded",
            "experience_required": "phd",
            "contact_email": "hci-lab@cmu.edu",
            "application_link": f"{base_url}/cmu-hci-postdoc/apply",
            "is_active": True,
            "location_city": "Pittsburgh",
            "location_state": "PA",
            "is_remote": False,
            "degree_levels": ["phd"],
            "min_hours": 40,
            "max_hours": 45,
            "paid_type": "stipend",
        },
        {
            "source_url": f"{base_url}/oxford-ml-healthcare",
            "title": "Research Assistant – Machine Learning for Healthcare",
            "description": (
                "Part-time research assistant position (20 hours per week) working on machine learning "
                "applications in healthcare. Projects involve developing predictive models for disease "
                "diagnosis, working with electronic health records, and ensuring model fairness and "
                "interpretability. A strong background in statistics and machine learning is required; "
                "experience with healthcare data is a plus. Remote work is possible for the right candidate. "
                "The role includes collaboration with clinicians and opportunities to publish in medical AI venues."
            ),
            "lab_name": "Oxford ML in Medicine",
            "pi_name": "Dr. Lisa Anderson",
            "institution": "University of Oxford",
            "research_topics": ["Healthcare AI", "Medical Imaging", "Predictive Modeling", "Fairness"],
            "methods": ["Deep Learning", "Bayesian Methods", "Federated Learning", "Survival Analysis"],
            "datasets": ["MIMIC", "ChestX-ray14", "UK Biobank"],
            "deadline": now + timedelta(days=20),
            "funding_status": "funded",
            "experience_required": "masters",
            "contact_email": "ml-health@oxford.ac.uk",
            "application_link": f"{base_url}/oxford-ml-healthcare/apply",
            "is_active": True,
            "location_city": "Oxford",
            "location_state": None,
            "is_remote": True,
            "degree_levels": ["masters", "phd"],
            "min_hours": 15,
            "max_hours": 20,
            "paid_type": "stipend",
        },
        {
            "source_url": f"{base_url}/toronto-ai-safety",
            "title": "PhD Position – AI Safety and Alignment",
            "description": (
                "Seeking PhD students interested in AI safety, alignment, and robustness research. "
                "Topics include adversarial robustness, out-of-distribution generalization, value alignment, "
                "and interpretability. Full funding is provided (tuition, stipend, research budget). "
                "Opportunities to attend top-tier conferences and collaborate with industry partners. "
                "Ideal candidates have strong mathematical and programming skills and a demonstrated "
                "interest in the long-term impact of AI systems."
            ),
            "lab_name": "Toronto AI Safety Lab",
            "pi_name": "Dr. David Kim",
            "institution": "University of Toronto",
            "research_topics": ["AI Safety", "Alignment", "Robustness", "Interpretability"],
            "methods": ["Adversarial Training", "Uncertainty Quantification", "RLHF", "Mechanistic Interpretability"],
            "datasets": ["ImageNet-C", "CIFAR-10-C", "Custom benchmarks"],
            "deadline": now + timedelta(days=14),
            "funding_status": "funded",
            "experience_required": "masters",
            "contact_email": "ai-safety@toronto.edu",
            "application_link": f"{base_url}/toronto-ai-safety/apply",
            "is_active": True,
            "location_city": "Toronto",
            "location_state": None,
            "is_remote": False,
            "degree_levels": ["masters", "phd"],
            "min_hours": 40,
            "max_hours": 50,
            "paid_type": "stipend",
        },
        {
            "source_url": f"{base_url}/harvard-compbio",
            "title": "Undergraduate Research – Computational Biology and Genomics",
            "description": (
                "We invite undergraduates to join our lab in computational biology and genomics. "
                "Projects include single-cell RNA sequencing analysis, variant effect prediction, and "
                "integrating multi-omics data for disease mapping. You will learn pipeline development, "
                "statistical modeling, and how to work with large genomic datasets. No prior wet-lab "
                "experience is required; strong interest in programming (Python/R) and biology is essential. "
                "This is a credit or paid position with flexible hours during the academic year."
            ),
            "lab_name": "Computational Genomics Lab",
            "pi_name": "Dr. Rachel Park",
            "institution": "Harvard University",
            "research_topics": ["Computational Biology", "Genomics", "Single-Cell", "Multi-Omics"],
            "methods": ["Statistical Modeling", "Pipeline Development", "Variant Calling", "Network Analysis"],
            "datasets": ["GTEx", "TCGA", "Single-cell atlases"],
            "deadline": now + timedelta(days=25),
            "funding_status": "funded",
            "experience_required": "undergraduate",
            "contact_email": "compbio@harvard.edu",
            "application_link": f"{base_url}/harvard-compbio/apply",
            "is_active": True,
            "location_city": "Cambridge",
            "location_state": "MA",
            "is_remote": False,
            "degree_levels": ["undergraduate"],
            "min_hours": 10,
            "max_hours": 20,
            "paid_type": "stipend",
        },
        {
            "source_url": f"{base_url}/princeton-econ-ml",
            "title": "Research Associate – Economics and Machine Learning",
            "description": (
                "The lab studies economic behavior and policy using machine learning and causal inference. "
                "We combine large-scale administrative data, field experiments, and structural models to "
                "answer questions in labor economics, education, and development. The role involves "
                "data cleaning, implementing estimators, running simulations, and co-authoring papers. "
                "Strong quantitative skills (econometrics, optimization, programming in Python/Stata/R) are "
                "required. Prior exposure to causal inference or ML is a plus. This is a one- to two-year "
                "pre-PhD research position."
            ),
            "lab_name": "Economics and ML Lab",
            "pi_name": "Dr. Thomas Wright",
            "institution": "Princeton University",
            "research_topics": ["Labor Economics", "Causal Inference", "Machine Learning", "Policy Evaluation"],
            "methods": ["Causal Inference", "Structural Estimation", "Field Experiments", "ML for Prediction"],
            "datasets": ["Administrative data", "Survey data", "Proprietary"],
            "deadline": now + timedelta(days=40),
            "funding_status": "funded",
            "experience_required": "undergraduate",
            "contact_email": "econ-ml@princeton.edu",
            "application_link": f"{base_url}/princeton-econ-ml/apply",
            "is_active": True,
            "location_city": "Princeton",
            "location_state": "NJ",
            "is_remote": False,
            "degree_levels": ["undergraduate", "masters"],
            "min_hours": 35,
            "max_hours": 40,
            "paid_type": "stipend",
        },
        {
            "source_url": f"{base_url}/caltech-climate",
            "title": "Graduate Research – Climate Science and Data Assimilation",
            "description": (
                "PhD or MS research position in climate science with a focus on data assimilation and "
                "earth system modeling. Work includes improving representation of clouds and convection "
                "in climate models, integrating satellite and in-situ observations, and quantifying "
                "uncertainty in projections. We use high-performance computing and modern ML techniques "
                "where appropriate. Background in atmospheric science, physics, applied math, or related "
                "fields is expected. Full funding is available for qualified applicants."
            ),
            "lab_name": "Climate Dynamics Group",
            "pi_name": "Dr. Maria Santos",
            "institution": "Caltech",
            "research_topics": ["Climate Science", "Data Assimilation", "Earth System Modeling", "Uncertainty Quantification"],
            "methods": ["Numerical Modeling", "Data Assimilation", "Statistical Downscaling", "ML for Climate"],
            "datasets": ["CMIP", "ERA5", "Satellite products", "Reanalyses"],
            "deadline": now + timedelta(days=50),
            "funding_status": "funded",
            "experience_required": "masters",
            "contact_email": "climate@caltech.edu",
            "application_link": f"{base_url}/caltech-climate/apply",
            "is_active": True,
            "location_city": "Pasadena",
            "location_state": "CA",
            "is_remote": False,
            "degree_levels": ["masters", "phd"],
            "min_hours": 40,
            "max_hours": 50,
            "paid_type": "stipend",
        },
        {
            "source_url": f"{base_url}/uw-speech-nlp",
            "title": "Research Assistant – Speech and Spoken Language Processing",
            "description": (
                "Join our group working on speech recognition, spoken dialogue systems, and low-resource "
                "language NLP. We combine signal processing, deep learning, and linguistic theory to build "
                "systems that work across accents, languages, and noisy conditions. Responsibilities include "
                "implementing and evaluating models, curating or annotating data, and writing up results. "
                "Experience with PyTorch, speech toolkits (e.g., Kaldi, ESPnet), or NLP is helpful. "
                "Both undergraduate and graduate applicants are welcome. Position can be remote or hybrid."
            ),
            "lab_name": "Spoken Language Systems Lab",
            "pi_name": "Dr. Jennifer Liu",
            "institution": "University of Washington",
            "research_topics": ["Speech Recognition", "Spoken Dialogue", "Low-Resource NLP", "Multilingual"],
            "methods": ["Deep Learning", "Signal Processing", "End-to-End Models", "Active Learning"],
            "datasets": ["LibriSpeech", "Common Voice", "Proprietary"],
            "deadline": now + timedelta(days=35),
            "funding_status": "funded",
            "experience_required": "undergraduate",
            "contact_email": "speech-nlp@uw.edu",
            "application_link": f"{base_url}/uw-speech-nlp/apply",
            "is_active": True,
            "location_city": "Seattle",
            "location_state": "WA",
            "is_remote": True,
            "degree_levels": ["undergraduate", "masters"],
            "min_hours": 15,
            "max_hours": 25,
            "paid_type": "stipend",
        },
        {
            "source_url": f"{base_url}/yale-neuro-ml",
            "title": "Postdoc or PhD – Neuroscience and Machine Learning",
            "description": (
                "We develop and apply machine learning methods to understand neural circuits and behavior. "
                "Projects include neural population dynamics, interpretable models of decision-making, and "
                "closed-loop brain–machine interfaces. You will work with large-scale neural recordings "
                "and behavioral data. Strong quantitative and programming skills (Python/MATLAB) are required; "
                "neuroscience background is beneficial but not mandatory. The lab is highly collaborative "
                "and supports career development. Funding is available for the right candidate."
            ),
            "lab_name": "Neural Computation Lab",
            "pi_name": "Dr. Alan Foster",
            "institution": "Yale University",
            "research_topics": ["Computational Neuroscience", "Neural Dynamics", "Decision-Making", "Brain–Machine Interfaces"],
            "methods": ["Dimensionality Reduction", "State-Space Models", "Deep Learning", "Bayesian Inference"],
            "datasets": ["Neural recordings", "Behavioral data", "Public atlases"],
            "deadline": now + timedelta(days=55),
            "funding_status": "funded",
            "experience_required": "phd",
            "contact_email": "neuro-ml@yale.edu",
            "application_link": f"{base_url}/yale-neuro-ml/apply",
            "is_active": True,
            "location_city": "New Haven",
            "location_state": "CT",
            "is_remote": False,
            "degree_levels": ["phd"],
            "min_hours": 40,
            "max_hours": 50,
            "paid_type": "stipend",
        },
        {
            "source_url": f"{base_url}/columbia-fairness",
            "title": "PhD or MS Research – Fairness, Accountability, and Transparency in AI",
            "description": (
                "We study fairness, accountability, and transparency in automated decision systems used in "
                "criminal justice, hiring, lending, and healthcare. Research includes formalizing and "
                "measuring fairness, auditing deployed systems, and designing interventions. We use methods "
                "from ML, law, and social science. Applicants should have strong technical skills and a "
                "genuine interest in the societal impact of AI. Experience with empirical research or "
                "policy is a plus. Funding is available for PhD students; MS students may apply for "
                "part-time or summer positions."
            ),
            "lab_name": "FAT ML Lab",
            "pi_name": "Dr. Nina Patel",
            "institution": "Columbia University",
            "research_topics": ["Fairness", "Accountability", "Transparency", "Algorithmic Auditing"],
            "methods": ["Fairness Metrics", "Auditing", "Causal Inference", "Participatory Methods"],
            "datasets": ["Proprietary", "Public benchmarks", "Survey data"],
            "deadline": now + timedelta(days=28),
            "funding_status": "funded",
            "experience_required": "masters",
            "contact_email": "fatml@columbia.edu",
            "application_link": f"{base_url}/columbia-fairness/apply",
            "is_active": True,
            "location_city": "New York",
            "location_state": "NY",
            "is_remote": False,
            "degree_levels": ["masters", "phd"],
            "min_hours": 30,
            "max_hours": 50,
            "paid_type": "stipend",
        },
        {
            "source_url": f"{base_url}/gatech-robotics-perception",
            "title": "Research Assistant – Robotic Perception and 3D Vision",
            "description": (
                "We are looking for a research assistant to work on 3D perception for robotics: scene "
                "understanding, object recognition, and spatial reasoning from RGB-D and LiDAR. Projects "
                "involve building and testing perception pipelines for mobile robots and manipulation. "
                "You will work with real robot platforms and simulation. Strong C++/Python skills and "
                "familiarity with ROS, OpenCV, or PyTorch are expected. This is a great opportunity for "
                "someone aiming for a robotics or vision PhD. Funding is available; position is on-site."
            ),
            "lab_name": "Robot Perception Lab",
            "pi_name": "Dr. Kevin Zhao",
            "institution": "Georgia Tech",
            "research_topics": ["3D Vision", "Robotic Perception", "Scene Understanding", "Object Recognition"],
            "methods": ["Deep Learning", "Point Cloud Processing", "SLAM", "Sim-to-Real"],
            "datasets": ["ScanNet", "ShapeNet", "Custom robot data"],
            "deadline": now + timedelta(days=42),
            "funding_status": "funded",
            "experience_required": "undergraduate",
            "contact_email": "robot-perception@gatech.edu",
            "application_link": f"{base_url}/gatech-robotics-perception/apply",
            "is_active": True,
            "location_city": "Atlanta",
            "location_state": "GA",
            "is_remote": False,
            "degree_levels": ["undergraduate", "masters"],
            "min_hours": 20,
            "max_hours": 30,
            "paid_type": "stipend",
        },
        {
            "source_url": f"{base_url}/uchicago-econ-experiments",
            "title": "Pre-Doctoral Fellow – Experimental and Behavioral Economics",
            "description": (
                "Pre-doctoral research position in experimental and behavioral economics. Work includes "
                "designing and running lab and field experiments, analyzing data, and developing theory. "
                "Topics range from market design and mechanism design to social preferences and belief "
                "formation. Proficiency in R or Python and experience with experiments or econometrics "
                "is preferred. This is a two-year position designed for those planning to apply to "
                "economics or related PhD programs. Competitive salary and benefits; some remote work possible."
            ),
            "lab_name": "Experimental Economics Lab",
            "pi_name": "Dr. Robert Hayes",
            "institution": "University of Chicago",
            "research_topics": ["Experimental Economics", "Behavioral Economics", "Market Design", "Mechanism Design"],
            "methods": ["Lab Experiments", "Field Experiments", "Econometrics", "Theory"],
            "datasets": ["Lab data", "Field data", "Administrative data"],
            "deadline": now + timedelta(days=33),
            "funding_status": "funded",
            "experience_required": "undergraduate",
            "contact_email": "expecon@uchicago.edu",
            "application_link": f"{base_url}/uchicago-econ-experiments/apply",
            "is_active": True,
            "location_city": "Chicago",
            "location_state": "IL",
            "is_remote": False,
            "degree_levels": ["undergraduate", "masters"],
            "min_hours": 40,
            "max_hours": 45,
            "paid_type": "stipend",
        },
        {
            "source_url": f"{base_url}/nyu-ml-systems",
            "title": "PhD Position – Machine Learning Systems and Efficiency",
            "description": (
                "PhD opening in efficient and scalable machine learning systems. Research spans model "
                "compression, distributed training, inference optimization, and hardware–software co-design. "
                "We work on both theory and implementation, often in collaboration with industry. Applicants "
                "should have strong systems and/or ML background (e.g., OS, compilers, distributed systems, "
                "or deep learning). Experience with PyTorch, CUDA, or large-scale training is a plus. "
                "Full funding including tuition and stipend is provided. The position is in NYC with "
                "optional hybrid arrangements."
            ),
            "lab_name": "Efficient ML Systems Lab",
            "pi_name": "Dr. Sophia Lee",
            "institution": "NYU",
            "research_topics": ["ML Systems", "Efficient Training", "Model Compression", "Distributed ML"],
            "methods": ["Compression", "Quantization", "Distributed Training", "Kernel Optimization"],
            "datasets": ["ImageNet", "Large-scale benchmarks", "Proprietary"],
            "deadline": now + timedelta(days=21),
            "funding_status": "funded",
            "experience_required": "masters",
            "contact_email": "ml-systems@nyu.edu",
            "application_link": f"{base_url}/nyu-ml-systems/apply",
            "is_active": True,
            "location_city": "New York",
            "location_state": "NY",
            "is_remote": False,
            "degree_levels": ["masters", "phd"],
            "min_hours": 40,
            "max_hours": 50,
            "paid_type": "stipend",
        },
    ]


def seed_opportunities():
    """Clear existing opportunities and insert 15 sample opportunities."""
    db = SessionLocal()
    try:
        # Clear existing opportunities
        deleted = db.query(Opportunity).delete()
        db.commit()
        print(f"Cleared {deleted} existing opportunity/opportunities.")

        # Insert all sample opportunities
        samples = get_sample_opportunities()
        for i, data in enumerate(samples, start=1):
            opp = Opportunity(**data)
            db.add(opp)
            print(f"  {i:2}. Added: {data['title'][:60]}...")
        db.commit()
        print(f"\nSeeding complete: {len(samples)} research opportunities inserted.")
    except Exception as e:
        db.rollback()
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_opportunities()
