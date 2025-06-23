/*
  Warnings:

  - You are about to drop the column `preview_url` on the `CV` table. All the data in the column will be lost.
  - You are about to drop the column `preview_url` on the `CVVersion` table. All the data in the column will be lost.

*/
-- AlterTable
ALTER TABLE "CV" DROP COLUMN "preview_url";

-- AlterTable
ALTER TABLE "CVVersion" DROP COLUMN "preview_url";
