
-- AlterTable
ALTER TABLE "CVVersion" ADD COLUMN     "parent_version_id" INTEGER;

-- AddForeignKey
ALTER TABLE "CVVersion" ADD CONSTRAINT "CVVersion_parent_version_id_fkey" FOREIGN KEY ("parent_version_id") REFERENCES "CVVersion"("id") ON DELETE SET NULL ON UPDATE CASCADE;
