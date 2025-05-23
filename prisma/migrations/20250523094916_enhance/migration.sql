/*
  Warnings:

  - You are about to drop the column `cv_id` on the `Certification` table. All the data in the column will be lost.
  - You are about to drop the column `cv_id` on the `Education` table. All the data in the column will be lost.
  - You are about to drop the column `cv_id` on the `Experience` table. All the data in the column will be lost.
  - You are about to drop the column `cv_id` on the `Project` table. All the data in the column will be lost.
  - You are about to drop the column `cv_id` on the `Publication` table. All the data in the column will be lost.
  - You are about to drop the column `cv_id` on the `TechnicalSkill` table. All the data in the column will be lost.

*/
-- DropForeignKey
ALTER TABLE "Certification" DROP CONSTRAINT "Certification_cv_id_fkey";

-- DropForeignKey
ALTER TABLE "Education" DROP CONSTRAINT "Education_cv_id_fkey";

-- DropForeignKey
ALTER TABLE "Experience" DROP CONSTRAINT "Experience_cv_id_fkey";

-- DropForeignKey
ALTER TABLE "Project" DROP CONSTRAINT "Project_cv_id_fkey";

-- DropForeignKey
ALTER TABLE "Publication" DROP CONSTRAINT "Publication_cv_id_fkey";

-- DropForeignKey
ALTER TABLE "TechnicalSkill" DROP CONSTRAINT "TechnicalSkill_cv_id_fkey";

-- AlterTable
ALTER TABLE "Certification" DROP COLUMN "cv_id";

-- AlterTable
ALTER TABLE "Education" DROP COLUMN "cv_id";

-- AlterTable
ALTER TABLE "Experience" DROP COLUMN "cv_id";

-- AlterTable
ALTER TABLE "Project" DROP COLUMN "cv_id";

-- AlterTable
ALTER TABLE "Publication" DROP COLUMN "cv_id";

-- AlterTable
ALTER TABLE "TechnicalSkill" DROP COLUMN "cv_id";

-- AlterTable
ALTER TABLE "User" ALTER COLUMN "created_at" SET DATA TYPE TIMESTAMP(3),
ALTER COLUMN "updated_at" SET DATA TYPE TIMESTAMP(3);

-- CreateTable
CREATE TABLE "CV_Education" (
    "cv_id" INTEGER NOT NULL,
    "education_id" INTEGER NOT NULL,

    CONSTRAINT "CV_Education_pkey" PRIMARY KEY ("cv_id","education_id")
);

-- CreateTable
CREATE TABLE "CV_Experience" (
    "cv_id" INTEGER NOT NULL,
    "experience_id" INTEGER NOT NULL,

    CONSTRAINT "CV_Experience_pkey" PRIMARY KEY ("cv_id","experience_id")
);

-- CreateTable
CREATE TABLE "CV_Certification" (
    "cv_id" INTEGER NOT NULL,
    "certification_id" INTEGER NOT NULL,

    CONSTRAINT "CV_Certification_pkey" PRIMARY KEY ("cv_id","certification_id")
);

-- CreateTable
CREATE TABLE "CV_Publication" (
    "cv_id" INTEGER NOT NULL,
    "publication_id" INTEGER NOT NULL,

    CONSTRAINT "CV_Publication_pkey" PRIMARY KEY ("cv_id","publication_id")
);

-- CreateTable
CREATE TABLE "CV_Project" (
    "cv_id" INTEGER NOT NULL,
    "project_id" INTEGER NOT NULL,

    CONSTRAINT "CV_Project_pkey" PRIMARY KEY ("cv_id","project_id")
);

-- CreateTable
CREATE TABLE "CV_TechnicalSkill" (
    "cv_id" INTEGER NOT NULL,
    "tech_skill_id" INTEGER NOT NULL,

    CONSTRAINT "CV_TechnicalSkill_pkey" PRIMARY KEY ("cv_id","tech_skill_id")
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

-- RenameForeignKey
ALTER TABLE "CVVersion" RENAME CONSTRAINT "fk_cvversion_allversions" TO "CVVersion_cv_id_fkey";

-- RenameForeignKey
ALTER TABLE "ResourceURL" RENAME CONSTRAINT "fk_resourceurl_projecturls" TO "FKEY_PROJECT_ID_RESOURCEURL_SOURCE_ID";

-- RenameForeignKey
ALTER TABLE "ResourceURL" RENAME CONSTRAINT "fk_resourceurl_publicationurls" TO "FKEY_PUBLICATION_ID_RESOURCEURL_SOURCE_ID";

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
ALTER TABLE "CV_TechnicalSkill" ADD CONSTRAINT "CV_TechnicalSkill_cv_id_fkey" FOREIGN KEY ("cv_id") REFERENCES "CV"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CV_TechnicalSkill" ADD CONSTRAINT "CV_TechnicalSkill_tech_skill_id_fkey" FOREIGN KEY ("tech_skill_id") REFERENCES "TechnicalSkill"("id") ON DELETE RESTRICT ON UPDATE CASCADE;

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
