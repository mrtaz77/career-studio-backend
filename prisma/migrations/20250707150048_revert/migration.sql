-- DropForeignKey
ALTER TABLE "CV" DROP CONSTRAINT "CV_latest_saved_version_id_fkey";

-- AlterTable
ALTER TABLE "CV" ALTER COLUMN "latest_saved_version_id" DROP NOT NULL,
ALTER COLUMN "latest_saved_version_id" DROP DEFAULT;

-- AddForeignKey
ALTER TABLE "CV" ADD CONSTRAINT "CV_latest_saved_version_id_fkey" FOREIGN KEY ("latest_saved_version_id") REFERENCES "CVVersion"("id") ON DELETE SET NULL ON UPDATE CASCADE;
