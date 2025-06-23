-- DropForeignKey
ALTER TABLE "CVVersion" DROP CONSTRAINT "CVVersion_cv_id_fkey";

-- DropForeignKey
ALTER TABLE "CV_Experience" DROP CONSTRAINT "CV_Experience_cv_id_fkey";

-- DropForeignKey
ALTER TABLE "CV_Project" DROP CONSTRAINT "CV_Project_cv_id_fkey";

-- DropForeignKey
ALTER TABLE "CV_Publication" DROP CONSTRAINT "CV_Publication_cv_id_fkey";

-- DropForeignKey
ALTER TABLE "CV_TechnicalSkill" DROP CONSTRAINT "CV_TechnicalSkill_cv_id_fkey";

-- AddForeignKey
ALTER TABLE "CV_Experience" ADD CONSTRAINT "CV_Experience_cv_id_fkey" FOREIGN KEY ("cv_id") REFERENCES "CV"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CV_Publication" ADD CONSTRAINT "CV_Publication_cv_id_fkey" FOREIGN KEY ("cv_id") REFERENCES "CV"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CV_Project" ADD CONSTRAINT "CV_Project_cv_id_fkey" FOREIGN KEY ("cv_id") REFERENCES "CV"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CV_TechnicalSkill" ADD CONSTRAINT "CV_TechnicalSkill_cv_id_fkey" FOREIGN KEY ("cv_id") REFERENCES "CV"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "CVVersion" ADD CONSTRAINT "CVVersion_cv_id_fkey" FOREIGN KEY ("cv_id") REFERENCES "CV"("id") ON DELETE CASCADE ON UPDATE CASCADE;
