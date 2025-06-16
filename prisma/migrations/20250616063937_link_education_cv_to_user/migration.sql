/*
  Warnings:

  - You are about to drop the `CV_Certification` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `CV_Education` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `Portfolio_Certification` table. If the table is not empty, all the data it contains will be lost.
  - You are about to drop the `Portfolio_Education` table. If the table is not empty, all the data it contains will be lost.
  - Added the required column `user_id` to the `Certification` table without a default value. This is not possible if the table is not empty.
  - Added the required column `user_id` to the `Education` table without a default value. This is not possible if the table is not empty.

*/
-- DropForeignKey
ALTER TABLE "CV_Certification" DROP CONSTRAINT "CV_Certification_certification_id_fkey";

-- DropForeignKey
ALTER TABLE "CV_Certification" DROP CONSTRAINT "CV_Certification_cv_id_fkey";

-- DropForeignKey
ALTER TABLE "CV_Education" DROP CONSTRAINT "CV_Education_cv_id_fkey";

-- DropForeignKey
ALTER TABLE "CV_Education" DROP CONSTRAINT "CV_Education_education_id_fkey";

-- DropForeignKey
ALTER TABLE "Portfolio_Certification" DROP CONSTRAINT "Portfolio_Certification_cert_id_fkey";

-- DropForeignKey
ALTER TABLE "Portfolio_Certification" DROP CONSTRAINT "Portfolio_Certification_portfolio_id_fkey";

-- DropForeignKey
ALTER TABLE "Portfolio_Education" DROP CONSTRAINT "Portfolio_Education_edu_id_fkey";

-- DropForeignKey
ALTER TABLE "Portfolio_Education" DROP CONSTRAINT "Portfolio_Education_portfolio_id_fkey";

-- AlterTable
ALTER TABLE "Certification" ADD COLUMN     "user_id" TEXT NOT NULL;

-- AlterTable
ALTER TABLE "Education" ADD COLUMN     "user_id" TEXT NOT NULL;

-- DropTable
DROP TABLE "CV_Certification";

-- DropTable
DROP TABLE "CV_Education";

-- DropTable
DROP TABLE "Portfolio_Certification";

-- DropTable
DROP TABLE "Portfolio_Education";

-- AddForeignKey
ALTER TABLE "Education" ADD CONSTRAINT "Education_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "User"("uid") ON DELETE RESTRICT ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Certification" ADD CONSTRAINT "Certification_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "User"("uid") ON DELETE RESTRICT ON UPDATE CASCADE;
