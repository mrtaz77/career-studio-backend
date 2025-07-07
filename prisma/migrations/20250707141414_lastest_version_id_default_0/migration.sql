/*
  Warnings:

  - Made the column `latest_saved_version_id` on table `CV` required. This step will fail if there are existing NULL values in that column.

*/
-- DropForeignKey
ALTER TABLE "CV" DROP CONSTRAINT "CV_latest_saved_version_id_fkey";

-- AlterTable
ALTER TABLE "CV" ALTER COLUMN "latest_saved_version_id" SET NOT NULL,
ALTER COLUMN "latest_saved_version_id" SET DEFAULT 0;

-- AddForeignKey
ALTER TABLE "CV" ADD CONSTRAINT "CV_latest_saved_version_id_fkey" FOREIGN KEY ("latest_saved_version_id") REFERENCES "CVVersion"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
