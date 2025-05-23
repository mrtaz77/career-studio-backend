-- CreateTable
CREATE TABLE "User" (
    "uid" TEXT NOT NULL,
    "username" TEXT NOT NULL,
    "full_name" TEXT NOT NULL,
    "email" TEXT NOT NULL,
    "address" TEXT NOT NULL,
    "phone" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "User_pkey" PRIMARY KEY ("uid")
);

-- CreateTable
CREATE TABLE "Education" (
    "id" SERIAL NOT NULL,
    "degree" TEXT NOT NULL,
    "institution" TEXT NOT NULL,
    "location" TEXT NOT NULL,
    "start_date" DATE NOT NULL,
    "end_date" DATE NOT NULL,
    "gpa" DOUBLE PRECISION NOT NULL,
    "honors" TEXT NOT NULL,

    CONSTRAINT "Education_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "CV_Education" (
    "cv_id" INTEGER NOT NULL,
    "education_id" INTEGER NOT NULL,

    CONSTRAINT "CV_Education_pkey" PRIMARY KEY ("cv_id","education_id")
);

-- CreateTable
CREATE TABLE "Experience" (
    "id" SERIAL NOT NULL,
    "job_title" TEXT NOT NULL,
    "position" TEXT NOT NULL,
    "company" TEXT NOT NULL,
    "company_url" TEXT NOT NULL,
    "company_logo" TEXT NOT NULL,
    "location" TEXT NOT NULL,
    "employment_type" TEXT NOT NULL,
    "location_type" TEXT NOT NULL,
    "industry" TEXT NOT NULL,
    "start_date" DATE NOT NULL,
    "end_date" DATE NOT NULL,
    "description" TEXT NOT NULL,

    CONSTRAINT "Experience_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "CV_Experience" (
    "cv_id" INTEGER NOT NULL,
    "experience_id" INTEGER NOT NULL,

    CONSTRAINT "CV_Experience_pkey" PRIMARY KEY ("cv_id","experience_id")
);

-- CreateTable
CREATE TABLE "Certification" (
    "id" SERIAL NOT NULL,
    "title" TEXT NOT NULL,
    "issuer" TEXT NOT NULL,
    "issued_date" DATE NOT NULL,
    "link" TEXT NOT NULL,

    CONSTRAINT "Certification_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "CV_Certification" (
    "cv_id" INTEGER NOT NULL,
    "certification_id" INTEGER NOT NULL,

    CONSTRAINT "CV_Certification_pkey" PRIMARY KEY ("cv_id","certification_id")
);

-- CreateTable
CREATE TABLE "Publication" (
    "id" SERIAL NOT NULL,
    "title" TEXT NOT NULL,
    "journal" TEXT NOT NULL,
    "year" INTEGER NOT NULL,
    "link" TEXT NOT NULL,

    CONSTRAINT "Publication_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "CV_Publication" (
    "cv_id" INTEGER NOT NULL,
    "publication_id" INTEGER NOT NULL,

    CONSTRAINT "CV_Publication_pkey" PRIMARY KEY ("cv_id","publication_id")
);

-- CreateTable
CREATE TABLE "Project" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "description" TEXT NOT NULL,

    CONSTRAINT "Project_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "CV_Project" (
    "cv_id" INTEGER NOT NULL,
    "project_id" INTEGER NOT NULL,

    CONSTRAINT "CV_Project_pkey" PRIMARY KEY ("cv_id","project_id")
);

-- CreateTable
CREATE TABLE "ProjectTechnology" (
    "id" SERIAL NOT NULL,
    "project_id" INTEGER NOT NULL,
    "technology" TEXT NOT NULL,

    CONSTRAINT "ProjectTechnology_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "ResourceURL" (
    "id" SERIAL NOT NULL,
    "source_id" INTEGER NOT NULL,
    "source_type" TEXT NOT NULL,
    "label" TEXT NOT NULL,
    "url" TEXT NOT NULL,

    CONSTRAINT "ResourceURL_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "TechnicalSkill" (
    "id" SERIAL NOT NULL,
    "name" TEXT NOT NULL,
    "category" TEXT NOT NULL,

    CONSTRAINT "TechnicalSkill_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "CV_TechnicalSkill" (
    "cv_id" INTEGER NOT NULL,
    "tech_skill_id" INTEGER NOT NULL,

    CONSTRAINT "CV_TechnicalSkill_pkey" PRIMARY KEY ("cv_id","tech_skill_id")
);

-- CreateTable
CREATE TABLE "CV" (
    "id" SERIAL NOT NULL,
    "user_id" TEXT NOT NULL,
    "type" TEXT NOT NULL,
    "bookmark" BOOLEAN NOT NULL DEFAULT false,
    "is_draft" BOOLEAN NOT NULL DEFAULT true,
    "pdf_url" TEXT,
    "preview_url" TEXT,
    "latest_saved_version_id" INTEGER,
    "created_at" TIMESTAMP(6) NOT NULL,
    "updated_at" TIMESTAMP(6) NOT NULL,

    CONSTRAINT "CV_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "CVVersion" (
    "id" SERIAL NOT NULL,
    "cv_id" INTEGER NOT NULL,
    "version_number" INTEGER NOT NULL,
    "pdf_url" TEXT NOT NULL,
    "preview_url" TEXT NOT NULL,
    "created_at" TIMESTAMP(6) NOT NULL,

    CONSTRAINT "CVVersion_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Portfolio" (
    "id" SERIAL NOT NULL,
    "user_id" TEXT NOT NULL,
    "theme" TEXT NOT NULL,
    "custom_domain" TEXT,
    "seo_meta" JSONB,
    "created_at" TIMESTAMP(3) NOT NULL,
    "updated_at" TIMESTAMP(3) NOT NULL,

    CONSTRAINT "Portfolio_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "PortfolioFeedback" (
    "id" SERIAL NOT NULL,
    "portfolio_id" INTEGER NOT NULL,
    "reviewer_id" TEXT,
    "reviewer_name" TEXT NOT NULL,
    "rating" INTEGER NOT NULL,
    "comment" TEXT NOT NULL,
    "created_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "PortfolioFeedback_pkey" PRIMARY KEY ("id")
);

-- CreateTable
CREATE TABLE "Portfolio_Education" (
    "portfolio_id" INTEGER NOT NULL,
    "edu_id" INTEGER NOT NULL,

    CONSTRAINT "Portfolio_Education_pkey" PRIMARY KEY ("portfolio_id","edu_id")
);

-- CreateTable
CREATE TABLE "Portfolio_Experience" (
    "portfolio_id" INTEGER NOT NULL,
    "exp_id" INTEGER NOT NULL,

    CONSTRAINT "Portfolio_Experience_pkey" PRIMARY KEY ("portfolio_id","exp_id")
);

-- CreateTable
CREATE TABLE "Portfolio_Project" (
    "portfolio_id" INTEGER NOT NULL,
    "project_id" INTEGER NOT NULL,
    "thumbnail_url" TEXT,

    CONSTRAINT "Portfolio_Project_pkey" PRIMARY KEY ("portfolio_id","project_id")
);

-- CreateTable
CREATE TABLE "Portfolio_Certification" (
    "portfolio_id" INTEGER NOT NULL,
    "cert_id" INTEGER NOT NULL,

    CONSTRAINT "Portfolio_Certification_pkey" PRIMARY KEY ("portfolio_id","cert_id")
);

-- CreateTable
CREATE TABLE "Portfolio_TechnicalSkill" (
    "portfolio_id" INTEGER NOT NULL,
    "tech_skill_id" INTEGER NOT NULL,

    CONSTRAINT "Portfolio_TechnicalSkill_pkey" PRIMARY KEY ("portfolio_id","tech_skill_id")
);

-- CreateTable
CREATE TABLE "Portfolio_Research" (
    "portfolio_id" INTEGER NOT NULL,
    "publication_id" INTEGER NOT NULL,
    "thumbnail_url" TEXT,
    "description" TEXT,

    CONSTRAINT "Portfolio_Research_pkey" PRIMARY KEY ("portfolio_id","publication_id")
);

-- CreateIndex
CREATE UNIQUE INDEX "User_username_key" ON "User"("username");

-- CreateIndex
CREATE UNIQUE INDEX "User_email_key" ON "User"("email");

-- AddForeignKey
ALTER TABLE "CV_Education" ADD CONSTRAINT "CV_Education_cv_id_fkey" FOREIGN KEY ("cv_id") REFERENCES "CV"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CV_Education" ADD CONSTRAINT "CV_Education_education_id_fkey" FOREIGN KEY ("education_id") REFERENCES "Education"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CV_Experience" ADD CONSTRAINT "CV_Experience_cv_id_fkey" FOREIGN KEY ("cv_id") REFERENCES "CV"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CV_Experience" ADD CONSTRAINT "CV_Experience_experience_id_fkey" FOREIGN KEY ("experience_id") REFERENCES "Experience"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CV_Certification" ADD CONSTRAINT "CV_Certification_cv_id_fkey" FOREIGN KEY ("cv_id") REFERENCES "CV"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CV_Certification" ADD CONSTRAINT "CV_Certification_certification_id_fkey" FOREIGN KEY ("certification_id") REFERENCES "Certification"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CV_Publication" ADD CONSTRAINT "CV_Publication_cv_id_fkey" FOREIGN KEY ("cv_id") REFERENCES "CV"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CV_Publication" ADD CONSTRAINT "CV_Publication_publication_id_fkey" FOREIGN KEY ("publication_id") REFERENCES "Publication"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CV_Project" ADD CONSTRAINT "CV_Project_cv_id_fkey" FOREIGN KEY ("cv_id") REFERENCES "CV"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CV_Project" ADD CONSTRAINT "CV_Project_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "Project"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ProjectTechnology" ADD CONSTRAINT "ProjectTechnology_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "Project"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ResourceURL" ADD CONSTRAINT "FKEY_PROJECT_ID_RESOURCEURL_SOURCE_ID" FOREIGN KEY ("source_id") REFERENCES "Project"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "ResourceURL" ADD CONSTRAINT "FKEY_PUBLICATION_ID_RESOURCEURL_SOURCE_ID" FOREIGN KEY ("source_id") REFERENCES "Publication"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CV_TechnicalSkill" ADD CONSTRAINT "CV_TechnicalSkill_cv_id_fkey" FOREIGN KEY ("cv_id") REFERENCES "CV"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CV_TechnicalSkill" ADD CONSTRAINT "CV_TechnicalSkill_tech_skill_id_fkey" FOREIGN KEY ("tech_skill_id") REFERENCES "TechnicalSkill"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CV" ADD CONSTRAINT "CV_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "User"("uid") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CV" ADD CONSTRAINT "CV_latest_saved_version_id_fkey" FOREIGN KEY ("latest_saved_version_id") REFERENCES "CVVersion"("id") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CVVersion" ADD CONSTRAINT "CVVersion_cv_id_fkey" FOREIGN KEY ("cv_id") REFERENCES "CV"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Portfolio" ADD CONSTRAINT "Portfolio_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "User"("uid") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "PortfolioFeedback" ADD CONSTRAINT "PortfolioFeedback_portfolio_id_fkey" FOREIGN KEY ("portfolio_id") REFERENCES "Portfolio"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "PortfolioFeedback" ADD CONSTRAINT "PortfolioFeedback_reviewer_id_fkey" FOREIGN KEY ("reviewer_id") REFERENCES "User"("uid") ON DELETE SET NULL ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Portfolio_Education" ADD CONSTRAINT "Portfolio_Education_portfolio_id_fkey" FOREIGN KEY ("portfolio_id") REFERENCES "Portfolio"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Portfolio_Education" ADD CONSTRAINT "Portfolio_Education_edu_id_fkey" FOREIGN KEY ("edu_id") REFERENCES "Education"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Portfolio_Experience" ADD CONSTRAINT "Portfolio_Experience_portfolio_id_fkey" FOREIGN KEY ("portfolio_id") REFERENCES "Portfolio"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Portfolio_Experience" ADD CONSTRAINT "Portfolio_Experience_exp_id_fkey" FOREIGN KEY ("exp_id") REFERENCES "Experience"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Portfolio_Project" ADD CONSTRAINT "Portfolio_Project_portfolio_id_fkey" FOREIGN KEY ("portfolio_id") REFERENCES "Portfolio"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Portfolio_Project" ADD CONSTRAINT "Portfolio_Project_project_id_fkey" FOREIGN KEY ("project_id") REFERENCES "Project"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Portfolio_Certification" ADD CONSTRAINT "Portfolio_Certification_portfolio_id_fkey" FOREIGN KEY ("portfolio_id") REFERENCES "Portfolio"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Portfolio_Certification" ADD CONSTRAINT "Portfolio_Certification_cert_id_fkey" FOREIGN KEY ("cert_id") REFERENCES "Certification"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Portfolio_TechnicalSkill" ADD CONSTRAINT "Portfolio_TechnicalSkill_portfolio_id_fkey" FOREIGN KEY ("portfolio_id") REFERENCES "Portfolio"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Portfolio_TechnicalSkill" ADD CONSTRAINT "Portfolio_TechnicalSkill_tech_skill_id_fkey" FOREIGN KEY ("tech_skill_id") REFERENCES "TechnicalSkill"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Portfolio_Research" ADD CONSTRAINT "Portfolio_Research_portfolio_id_fkey" FOREIGN KEY ("portfolio_id") REFERENCES "Portfolio"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Portfolio_Research" ADD CONSTRAINT "Portfolio_Research_publication_id_fkey" FOREIGN KEY ("publication_id") REFERENCES "Publication"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
