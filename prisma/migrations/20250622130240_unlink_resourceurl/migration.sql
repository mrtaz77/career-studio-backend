-- DropForeignKey
ALTER TABLE "ResourceURL" DROP CONSTRAINT "FKEY_PROJECT_ID_RESOURCEURL_SOURCE_ID";

-- DropForeignKey
ALTER TABLE "ResourceURL" DROP CONSTRAINT "FKEY_PUBLICATION_ID_RESOURCEURL_SOURCE_ID";

-- CreateIndex
CREATE INDEX "ResourceURL_source_id_source_type_idx" ON "ResourceURL"("source_id", "source_type");
