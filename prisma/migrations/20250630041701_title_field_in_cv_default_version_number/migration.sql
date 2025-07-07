-- AlterTable
ALTER TABLE "CV" ADD COLUMN     "title" TEXT NOT NULL DEFAULT 'Untitled CV';

-- AlterTable
ALTER TABLE "CVVersion" ALTER COLUMN "version_number" SET DEFAULT 0;
