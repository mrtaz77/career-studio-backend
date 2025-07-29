/*
  Warnings:

  - You are about to drop the `Portfolio_Research` table. If the table is not empty, all the data it contains will be lost.

*/
-- DropForeignKey
ALTER TABLE "Portfolio_Research" DROP CONSTRAINT "Portfolio_Research_portfolio_id_fkey";

-- DropForeignKey
ALTER TABLE "Portfolio_Research" DROP CONSTRAINT "Portfolio_Research_publication_id_fkey";

-- DropTable
DROP TABLE "Portfolio_Research";

-- CreateTable
CREATE TABLE "Portfolio_Publication" (
    "portfolio_id" INTEGER NOT NULL,
    "publication_id" INTEGER NOT NULL,

    CONSTRAINT "Portfolio_Publication_pkey" PRIMARY KEY ("portfolio_id","publication_id")
);

-- AddForeignKey
ALTER TABLE "Portfolio_Publication" ADD CONSTRAINT "Portfolio_Publication_portfolio_id_fkey" FOREIGN KEY ("portfolio_id") REFERENCES "Portfolio"("id") ON DELETE CASCADE ON UPDATE CASCADE;

-- AddForeignKey
ALTER TABLE "Portfolio_Publication" ADD CONSTRAINT "Portfolio_Publication_publication_id_fkey" FOREIGN KEY ("publication_id") REFERENCES "Publication"("id") ON DELETE RESTRICT ON UPDATE CASCADE;
