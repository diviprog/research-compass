"""
Seed script to add sample research opportunities to the database.
Run this to populate your database with test data.
"""

from datetime import datetime, timedelta
from app.db.database import SessionLocal
from app.models.opportunity import Opportunity


def seed_opportunities():
    """Add sample research opportunities to the database."""
    
    db = SessionLocal()
    
    sample_opportunities = [
        {
            "source_url": "https://example.com/mit-vision-lab",
            "title": "Research Assistant - Computer Vision Lab",
            "description": """We are seeking a motivated research assistant to work on cutting-edge computer vision projects. 
            
The position involves developing novel deep learning architectures for multimodal learning, working with large-scale image and video datasets, and contributing to publication-quality research. 

Ideal candidates should have strong programming skills in Python, experience with PyTorch or TensorFlow, and a passion for advancing the state-of-the-art in computer vision.""",
            "lab_name": "Vision Intelligence Lab",
            "pi_name": "Dr. Sarah Chen",
            "institution": "MIT",
            "research_topics": ["Computer Vision", "Deep Learning", "Multimodal Learning"],
            "methods": ["Neural Networks", "Transformers", "Self-Supervised Learning"],
            "datasets": ["ImageNet", "COCO", "LAION"],
            "deadline": datetime.now() + timedelta(days=30),
            "funding_status": "funded",
            "experience_required": "undergraduate",
            "contact_email": "visionlab@mit.edu",
            "application_link": "https://example.com/apply/vision-lab",
            "is_active": True
        },
        {
            "source_url": "https://example.com/stanford-nlp",
            "title": "PhD Student Opening - Natural Language Processing",
            "description": """Fully funded PhD position available in Natural Language Processing with focus on large language models and their applications.

Projects include research on efficient fine-tuning methods, interpretability of transformer models, and applications in healthcare and education domains.

We offer competitive stipend, full tuition coverage, and opportunities to collaborate with leading researchers in the field.""",
            "lab_name": "Stanford NLP Group",
            "pi_name": "Dr. Michael Zhang",
            "institution": "Stanford University",
            "research_topics": ["NLP", "Large Language Models", "AI Safety"],
            "methods": ["Transformers", "Fine-tuning", "Prompt Engineering"],
            "datasets": ["C4", "The Pile", "GLUE"],
            "deadline": datetime.now() + timedelta(days=15),
            "funding_status": "funded",
            "experience_required": "masters",
            "contact_email": "nlp-recruiting@stanford.edu",
            "application_link": "https://example.com/apply/stanford-nlp",
            "is_active": True
        },
        {
            "source_url": "https://example.com/berkeley-robotics",
            "title": "Summer Research Internship - Robotics and Manipulation",
            "description": """10-week summer research internship focused on robotic manipulation using reinforcement learning and imitation learning.

Interns will work on real robotic systems, develop simulation environments, and contribute to ongoing research projects. This is an excellent opportunity for undergraduates interested in pursuing graduate studies in robotics.

Prior experience with ROS, Python, and basic machine learning is preferred but not required.""",
            "lab_name": "Berkeley Robot Learning Lab",
            "pi_name": "Dr. Emma Rodriguez",
            "institution": "UC Berkeley",
            "research_topics": ["Robotics", "Reinforcement Learning", "Manipulation"],
            "methods": ["RL", "Imitation Learning", "Sim-to-Real Transfer"],
            "datasets": ["D4RL", "RoboNet"],
            "deadline": datetime.now() + timedelta(days=45),
            "funding_status": "funded",
            "experience_required": "undergraduate",
            "contact_email": "robotics@berkeley.edu",
            "is_active": True
        },
        {
            "source_url": "https://example.com/cmu-hci",
            "title": "Postdoctoral Researcher - Human-Computer Interaction",
            "description": """We are seeking a postdoctoral researcher to join our lab studying the intersection of AI and human-computer interaction.

Research areas include:
- AI-assisted design and creativity tools
- Explainable AI interfaces
- User studies and evaluation methods
- Collaborative human-AI systems

The position is for 2 years with possibility of extension. Competitive salary and benefits package included.""",
            "lab_name": "Human-AI Interaction Lab",
            "pi_name": "Dr. James Williams",
            "institution": "Carnegie Mellon University",
            "research_topics": ["HCI", "AI", "UX Design"],
            "methods": ["User Studies", "Prototyping", "A/B Testing"],
            "datasets": [],
            "deadline": datetime.now() + timedelta(days=60),
            "funding_status": "funded",
            "experience_required": "phd",
            "contact_email": "hci-lab@cmu.edu",
            "application_link": "https://example.com/apply/cmu-hci",
            "is_active": True
        },
        {
            "source_url": "https://example.com/oxford-ml",
            "title": "Research Assistant - Machine Learning for Healthcare",
            "description": """Part-time research assistant position (20 hours/week) working on machine learning applications in healthcare.

Projects involve developing predictive models for disease diagnosis, working with electronic health records, and ensuring model fairness and interpretability.

Strong background in statistics and machine learning required. Experience with healthcare data is a plus. Remote work possible.""",
            "lab_name": "Oxford Machine Learning in Medicine",
            "pi_name": "Dr. Lisa Anderson",
            "institution": "University of Oxford",
            "research_topics": ["Healthcare AI", "Medical Imaging", "Predictive Modeling"],
            "methods": ["Deep Learning", "Bayesian Methods", "Federated Learning"],
            "datasets": ["MIMIC", "ChestX-ray14"],
            "deadline": datetime.now() + timedelta(days=20),
            "funding_status": "funded",
            "experience_required": "masters",
            "contact_email": "ml-health@oxford.ac.uk",
            "application_link": "https://example.com/apply/oxford-ml",
            "is_active": True
        },
        {
            "source_url": "https://example.com/toronto-ai-safety",
            "title": "PhD Position - AI Safety and Alignment",
            "description": """Seeking PhD students interested in AI safety, alignment, and robustness research.

Research topics include:
- Adversarial robustness
- Out-of-distribution generalization
- Value alignment
- Interpretability and explainability

Full funding provided including tuition, stipend, and research budget. Opportunities to attend top-tier conferences and collaborate with industry partners.""",
            "lab_name": "Toronto AI Safety Lab",
            "pi_name": "Dr. David Kim",
            "institution": "University of Toronto",
            "research_topics": ["AI Safety", "Alignment", "Robustness"],
            "methods": ["Adversarial Training", "Uncertainty Quantification", "RLHF"],
            "datasets": ["ImageNet-C", "CIFAR-10-C"],
            "deadline": datetime.now() + timedelta(days=5),
            "funding_status": "funded",
            "experience_required": "masters",
            "contact_email": "ai-safety@toronto.edu",
            "application_link": "https://example.com/apply/toronto-safety",
            "is_active": True
        }
    ]
    
    print("🌱 Seeding research opportunities...")
    
    for opp_data in sample_opportunities:
        # Check if opportunity with this URL already exists
        existing = db.query(Opportunity).filter(
            Opportunity.source_url == opp_data["source_url"]
        ).first()
        
        if existing:
            print(f"   ⏭️  Skipping '{opp_data['title']}' - already exists")
            continue
        
        opportunity = Opportunity(**opp_data)
        db.add(opportunity)
        print(f"   ✅ Added: {opp_data['title']}")
    
    db.commit()
    db.close()
    
    print("✨ Seeding complete!")


if __name__ == "__main__":
    seed_opportunities()

