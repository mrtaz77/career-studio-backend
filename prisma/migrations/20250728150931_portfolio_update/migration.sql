/*
  Warnings:

  - A unique constraint covering the columns `[published_url]` on the table `Portfolio` will be added. If there are existing duplicate values, this will fail.
  - Added the required column `title` to the `Portfolio` table without a default value. This is not possible if the table is not empty.

*/
-- DropForeignKey
ALTER TABLE "PortfolioFeedback" DROP CONSTRAINT "PortfolioFeedback_portfolio_id_fkey";

-- DropForeignKey
ALTER TABLE "Portfolio_Experience" DROP CONSTRAINT "Portfolio_Experience_portfolio_id_fkey";

-- DropForeignKey
ALTER TABLE "Portfolio_Project" DROP CONSTRAINT "Portfolio_Project_portfolio_id_fkey";

-- DropForeignKey
ALTER TABLE "Portfolio_Research" DROP CONSTRAINT "Portfolio_Research_portfolio_id_fkey";

-- DropForeignKey
ALTER TABLE "Portfolio_TechnicalSkill" DROP CONSTRAINT "Portfolio_TechnicalSkill_portfolio_id_fkey";

-- AlterTable
ALTER TABLE "Portfolio" ADD COLUMN     "bio" TEXT,
ADD COLUMN     "is_public" BOOLEAN NOT NULL DEFAULT false,
ADD COLUMN     "published_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,
ADD COLUMN     "published_url" TEXT,
ADD COLUMN     "title" TEXT NOT NULL;

-- CreateIndex
CREATE UNIQUE INDEX "Portfolio_published_url_key" ON "Portfolio"("published_url");

-- AddForeignKey
ALTER TABLE "PortfolioFeedback" ADD CONSTRAINT "PortfolioFeedback_portfolio_id_fkey" FOREIGN KEY ("portfolio_id") REFERENCES "Portfolio"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Portfolio_Experience" ADD CONSTRAINT "Portfolio_Experience_portfolio_id_fkey" FOREIGN KEY ("portfolio_id") REFERENCES "Portfolio"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Portfolio_Project" ADD CONSTRAINT "Portfolio_Project_portfolio_id_fkey" FOREIGN KEY ("portfolio_id") REFERENCES "Portfolio"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Portfolio_TechnicalSkill" ADD CONSTRAINT "Portfolio_TechnicalSkill_portfolio_id_fkey" FOREIGN KEY ("portfolio_id") REFERENCES "Portfolio"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Portfolio_Research" ADD CONSTRAINT "Portfolio_Research_portfolio_id_fkey" FOREIGN KEY ("portfolio_id") REFERENCES "Portfolio"("id") ON DELETE CASCADE ON UPDATE CASCADE;
