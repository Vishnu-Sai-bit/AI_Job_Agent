# Database Schema Specifications

## 1. Relational Entities
- **users**: `id` (PK), `email`, `password_hash`, `full_name`, `role`, `created_at`
- **candidate_profiles**: `id` (PK), `user_id` (FK), `preferred_role`, `preferred_location`, `experience_years`, `skills` (JSON), `education` (JSON), `projects` (JSON), `certifications` (JSON), `ats_score`
- **jobs**: `id` (PK), `title`, `company`, `location`, `salary`, `experience`, `source`, `url`, `skills` (JSON), `description`
- **job_matches**: `id` (PK), `user_id` (FK), `job_id` (FK), `match_score`, `role_fit`, `skill_fit`, `matching_skills` (JSON), `missing_skills` (JSON)
- **applications**: `id` (PK), `user_id` (FK), `job_id` (FK), `company`, `role`, `stage`, `applied_date`, `notes`
- **interviews**: `id` (PK), `user_id` (FK), `role`, `company`, `round_type`, `questions_data` (JSON), `score`, `feedback`
- **learning_plans**: `id` (PK), `user_id` (FK), `target_role`, `skill_gaps` (JSON), `roadmaps_data` (JSON)
- **notifications**: `id` (PK), `user_id` (FK), `title`, `message`, `category`, `is_read`, `created_at`
- **automations**: `id` (PK), `user_id` (FK), `daily_digest`, `min_match_threshold`, `followup_reminder_days`, `email_alerts`
