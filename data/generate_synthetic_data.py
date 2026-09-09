import os
import random
import json
from datetime import datetime, timedelta

DATA_DIR = os.path.dirname(os.path.abspath(__file__))

WORK_MODES = ["Remote", "Hybrid", "On-site"]
LANGUAGES = ["English-primary", "Multilingual/non-English-primary"]
REGIONS = ["North America", "EMEA", "APAC", "LATAM"]
AGE_GROUPS = ["18-25", "26-35", "36-50", "51+"]

CATEGORIES = [
    "workplace",
    "financial",
    "family",
    "wellbeing",
    "housing",
    "legal_support",
    "general_progress"
]

SAMPLE_SESSION_TEMPLATES = {
    "workplace": [
        "Client discussed high workload, deadline pressure, and communication tension with team management.",
        "Client reported experiencing burnout due to overtime hours and performance metrics concerns.",
        "Client shared feelings of role ambiguity and conflict with a project lead."
    ],
    "financial": [
        "Client expressed distress over debt accumulation, budgeting challenges, and cost of living increases.",
        "Client requested assistance regarding financial planning resources and emergency loan options.",
        "Client discussed salary negotiation anxiety and unexpected medical expenses burden."
    ],
    "family": [
        "Client shared ongoing marital strain, caregiving responsibilities for aging parents, and childcare logistics.",
        "Client discussed family communication breakdown and recent grief following a family bereavement.",
        "Client expressed concerns regarding adolescent child behavior and domestic routine stress."
    ],
    "wellbeing": [
        "Client reported sleep disturbances, generalized anxiety symptoms, and difficulty switching off after work.",
        "Client discussed mindfulness practices, stress coping mechanisms, and physical exercise goals.",
        "Client shared improvement in self-care routines but occasional panic symptoms before presentations."
    ],
    "housing": [
        "Client expressed concern about lease renewal, landlord dispute, and housing instability.",
        "Client discussed relocation stress due to remote work policy change and rent affordability.",
        "Client sought guidance on tenant rights and community housing assistance programs."
    ],
    "legal_support": [
        "Client inquired about legal advice for contract dispute and divorce proceedings guidance.",
        "Client mentioned needing legal aid referral for tenancy dispute.",
        "Client discussed legal documentation requirements for family estate management."
    ],
    "general_progress": [
        "Client reviewed overall goals and noted moderate improvement in daily stress management.",
        "Client actively participated in session and established new boundary setting strategies.",
        "Client expressed satisfaction with current progress and agreed to bi-weekly check-ins."
    ]
}

def generate_data(num_clients=200, num_counsellors=15, num_social_workers=8):
    random.seed(42)
    now = datetime.utcnow()

    # 1. Staff
    counsellors = []
    for i in range(1, num_counsellors + 1):
        c_id = f"COUNS_{i:03d}"
        max_cases = random.randint(15, 25)
        curr_cases = random.randint(5, max_cases)
        counsellors.append({
            "staff_id": c_id,
            "name": f"Counsellor {i}",
            "role": "counsellor",
            "maximum_active_cases": max_cases,
            "current_active_cases": curr_cases,
            "available_slots": max_cases - curr_cases
        })

    social_workers = []
    for i in range(1, num_social_workers + 1):
        sw_id = f"SOC_{i:03d}"
        max_cases = random.randint(10, 20)
        curr_cases = random.randint(3, max_cases)
        social_workers.append({
            "staff_id": sw_id,
            "name": f"Social Worker {i}",
            "role": "social_worker",
            "maximum_active_cases": max_cases,
            "current_active_cases": curr_cases,
            "available_slots": max_cases - curr_cases
        })

    # Ensure Soc Worker 1 has capacity for C001 demo
    social_workers[0]["current_active_cases"] = 5
    social_workers[0]["available_slots"] = 10

    # 2. Clients
    clients = []

    # Demographically structured Demo Client C001
    clients.append({
        "client_id": "C001",
        "age_group": "26-35",
        "work_mode": "Hybrid",
        "preferred_language": "English-primary",
        "region": "North America",
        "created_at": (now - timedelta(days=90)).isoformat()
    })

    for i in range(2, num_clients + 1):
        c_id = f"C{i:03d}"
        clients.append({
            "client_id": c_id,
            "age_group": random.choice(AGE_GROUPS),
            "work_mode": random.choice(WORK_MODES),
            "preferred_language": random.choice(LANGUAGES),
            "region": random.choice(REGIONS),
            "created_at": (now - timedelta(days=random.randint(10, 180))).isoformat()
        })

    # 3. Consents
    consents = []

    # Demo Client C001 Consent Setup (Section 25)
    # Workplace -> SHARE counsellor
    consents.append({
        "consent_id": "CNS_C001_1",
        "client_id": "C001",
        "information_category": "workplace",
        "allowed_recipient_role": "counsellor",
        "consent_status": "granted",
        "granted_at": (now - timedelta(days=80)).isoformat(),
        "revoked_at": None
    })
    # Financial -> SHARE social_worker
    consents.append({
        "consent_id": "CNS_C001_2",
        "client_id": "C001",
        "information_category": "financial",
        "allowed_recipient_role": "social_worker",
        "consent_status": "granted",
        "granted_at": (now - timedelta(days=80)).isoformat(),
        "revoked_at": None
    })
    # Wellbeing -> SHARE all
    consents.append({
        "consent_id": "CNS_C001_3",
        "client_id": "C001",
        "information_category": "wellbeing",
        "allowed_recipient_role": "all",
        "consent_status": "granted",
        "granted_at": (now - timedelta(days=80)).isoformat(),
        "revoked_at": None
    })
    # Family -> DO NOT SHARE (Revoked / Restricted)
    consents.append({
        "consent_id": "CNS_C001_4",
        "client_id": "C001",
        "information_category": "family",
        "allowed_recipient_role": "all",
        "consent_status": "revoked",
        "granted_at": (now - timedelta(days=80)).isoformat(),
        "revoked_at": (now - timedelta(days=10)).isoformat()
    })

    # Generic consents for C002-C200
    consent_id_counter = 100
    for client in clients[1:]:
        c_id = client["client_id"]
        for cat in CATEGORIES:
            # Randomly grant or revoke consent with different recipient roles
            if random.random() < 0.65:
                role = random.choice(["counsellor", "social_worker", "all"])
                consents.append({
                    "consent_id": f"CNS_{consent_id_counter}",
                    "client_id": c_id,
                    "information_category": cat,
                    "allowed_recipient_role": role,
                    "consent_status": "granted",
                    "granted_at": (now - timedelta(days=random.randint(20, 100))).isoformat(),
                    "revoked_at": None
                })
                consent_id_counter += 1
            elif random.random() < 0.15:
                role = random.choice(["counsellor", "social_worker", "all"])
                consents.append({
                    "consent_id": f"CNS_{consent_id_counter}",
                    "client_id": c_id,
                    "information_category": cat,
                    "allowed_recipient_role": role,
                    "consent_status": "revoked",
                    "granted_at": (now - timedelta(days=random.randint(40, 100))).isoformat(),
                    "revoked_at": (now - timedelta(days=random.randint(1, 20))).isoformat()
                })
                consent_id_counter += 1

    # 4. Sessions (~800 total)
    sessions = []
    session_counter = 1

    # C001 sessions specifically referencing workplace stress, family conflict, financial difficulty
    sessions.append({
        "session_id": "SESS_C001_1",
        "client_id": "C001",
        "counsellor_id": "COUNS_001",
        "session_date": (now - timedelta(days=45)).strftime("%Y-%m-%d"),
        "session_summary": "Client discussed workplace pressure and family conflict in detail during initial intake session.",
        "sensitivity_level": "High",
        "created_at": (now - timedelta(days=45)).isoformat()
    })
    sessions.append({
        "session_id": "SESS_C001_2",
        "client_id": "C001",
        "counsellor_id": "COUNS_001",
        "session_date": (now - timedelta(days=20)).strftime("%Y-%m-%d"),
        "session_summary": "Client expressed severe financial difficulty regarding rent escalation and debt repayment planning.",
        "sensitivity_level": "Medium",
        "created_at": (now - timedelta(days=20)).isoformat()
    })
    sessions.append({
        "session_id": "SESS_C001_3",
        "client_id": "C001",
        "counsellor_id": "COUNS_001",
        "session_date": (now - timedelta(days=5)).strftime("%Y-%m-%d"),
        "session_summary": "Client reviewed wellbeing goals, reported ongoing workplace strain, and asked for handover to social worker for financial housing support.",
        "sensitivity_level": "Medium",
        "created_at": (now - timedelta(days=5)).isoformat()
    })

    # Sessions for other clients
    for client in clients[1:]:
        c_id = client["client_id"]
        num_sess = random.randint(2, 5)
        for s in range(num_sess):
            couns = random.choice(counsellors)["staff_id"]
            sess_date = now - timedelta(days=random.randint(2, 120))
            cats = random.sample(CATEGORIES, random.randint(1, 3))
            summaries = [random.choice(SAMPLE_SESSION_TEMPLATES[c]) for c in cats]
            combined_summary = " ".join(summaries)
            sessions.append({
                "session_id": f"SESS_{session_counter:04d}",
                "client_id": c_id,
                "counsellor_id": couns,
                "session_date": sess_date.strftime("%Y-%m-%d"),
                "session_summary": combined_summary,
                "sensitivity_level": random.choice(["Low", "Medium", "High"]),
                "created_at": sess_date.isoformat()
            })
            session_counter += 1

    # 5. Client Goals
    goals = []
    goal_counter = 1

    # C001 goals
    goals.append({
        "goal_id": "GOAL_C001_1",
        "client_id": "C001",
        "goal_category": "workplace",
        "goal_description": "Develop workload boundary setting techniques and reduce burnout symptoms.",
        "goal_status": "Active",
        "created_at": (now - timedelta(days=40)).isoformat()
    })
    goals.append({
        "goal_id": "GOAL_C001_2",
        "client_id": "C001",
        "goal_category": "financial",
        "goal_description": "Establish sustainable budget and connect with financial counseling advisor.",
        "goal_status": "Active",
        "created_at": (now - timedelta(days=20)).isoformat()
    })

    for client in clients[1:]:
        c_id = client["client_id"]
        num_g = random.randint(1, 3)
        for _ in range(num_g):
            cat = random.choice(CATEGORIES)
            goals.append({
                "goal_id": f"GOAL_{goal_counter:04d}",
                "client_id": c_id,
                "goal_category": cat,
                "goal_description": f"Improve stability and outcomes regarding {cat.replace('_', ' ')}.",
                "goal_status": random.choice(["Active", "Active", "Achieved", "Paused"]),
                "created_at": (now - timedelta(days=random.randint(10, 90))).isoformat()
            })
            goal_counter += 1

    # 6. Pending Actions
    actions = []
    action_counter = 1

    # C001 pending action for social worker
    actions.append({
        "action_id": "ACT_C001_1",
        "client_id": "C001",
        "assigned_role": "social_worker",
        "action_description": "Assist client with financial grant application and housing budgeting resources.",
        "priority": "High",
        "due_date": (now + timedelta(days=7)).strftime("%Y-%m-%d"),
        "status": "Pending"
    })

    for client in clients[1:]:
        c_id = client["client_id"]
        if random.random() < 0.7:
            role = random.choice(["counsellor", "social_worker"])
            actions.append({
                "action_id": f"ACT_{action_counter:04d}",
                "client_id": c_id,
                "assigned_role": role,
                "action_description": f"Follow up on {random.choice(CATEGORIES).replace('_', ' ')} assistance plan.",
                "priority": random.choice(["High", "Medium", "Low"]),
                "due_date": (now + timedelta(days=random.randint(2, 14))).strftime("%Y-%m-%d"),
                "status": random.choice(["Pending", "In Progress", "Completed"])
            })
            action_counter += 1

    # Save to JSON / CSV files in data/ directory
    dataset = {
        "clients": clients,
        "counsellors": counsellors,
        "social_workers": social_workers,
        "consents": consents,
        "sessions": sessions,
        "goals": goals,
        "actions": actions
    }

    output_file = os.path.join(DATA_DIR, "synthetic_dataset.json")
    with open(output_file, "w") as f:
        json.dump(dataset, f, indent=2)

    print(f"Dataset generated successfully at {output_file}:")
    print(f" - Clients: {len(clients)}")
    print(f" - Counsellors: {len(counsellors)}")
    print(f" - Social Workers: {len(social_workers)}")
    print(f" - Sessions: {len(sessions)}")
    print(f" - Goals: {len(goals)}")
    print(f" - Consents: {len(consents)}")
    print(f" - Actions: {len(actions)}")
    return dataset

if __name__ == "__main__":
    generate_data()
