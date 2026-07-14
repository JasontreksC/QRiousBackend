-- QRious DB Schema
-- Based on ERD: Student, Charm, Have, Want, ExHave, ExWant
-- API: student_id는 학번(TEXT 10자리), charm_id만 UUID

CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 신청자 기본 정보
CREATE TABLE IF NOT EXISTS student (
    student_id  TEXT PRIMARY KEY,           -- 학번
    name        TEXT,                       -- 이름
    gender      BOOLEAN DEFAULT FALSE,      -- 성별 (false=남자, true=여자)
    age         INTEGER,                    -- 나이
    mbti        TEXT                        -- MBTI
);

-- 매력(속성) 마스터
CREATE TABLE IF NOT EXISTS charm (
    charm_id    UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name        TEXT                        -- 매력이름
);

-- 신청자의 매력 (다대다)
CREATE TABLE IF NOT EXISTS have (
    student_id  TEXT NOT NULL REFERENCES student (student_id) ON DELETE CASCADE,
    charm_id    UUID NOT NULL REFERENCES charm (charm_id) ON DELETE CASCADE,
    PRIMARY KEY (student_id, charm_id)
);

-- 신청자의 이상형 매력 (다대다)
CREATE TABLE IF NOT EXISTS want (
    student_id  TEXT NOT NULL REFERENCES student (student_id) ON DELETE CASCADE,
    charm_id    UUID NOT NULL REFERENCES charm (charm_id) ON DELETE CASCADE,
    PRIMARY KEY (student_id, charm_id)
);

-- 추가 어필 매력 (1:1 자유 텍스트)
CREATE TABLE IF NOT EXISTS ex_have (
    student_id  TEXT PRIMARY KEY REFERENCES student (student_id) ON DELETE CASCADE,
    charm       TEXT                        -- 매력 텍스트
);

-- 추가 원하는 이상형 (1:1 자유 텍스트)
CREATE TABLE IF NOT EXISTS ex_want (
    student_id  TEXT PRIMARY KEY REFERENCES student (student_id) ON DELETE CASCADE,
    charm       TEXT                        -- 매력 텍스트
);

CREATE INDEX IF NOT EXISTS idx_have_charm_id ON have (charm_id);
CREATE INDEX IF NOT EXISTS idx_want_charm_id ON want (charm_id);
