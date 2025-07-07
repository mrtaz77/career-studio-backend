/*
  Warnings:

  - Added the required column `title` to the `CV` table without a default value. This is not possible if the table is not empty.

*/

-- CreateTable
CREATE TABLE "Achievement" (
    "id" SERIAL NOT NULL,
    "user_id" TEXT NOT NULL,
    "description" TEXT NOT NULL,

    CONSTRAINT "Achievement_pkey" PRIMARY KEY ("id")
);

-- AddForeignKey
ALTER TABLE "Achievement" ADD CONSTRAINT "Achievement_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "User"("uid") ON DELETE RESTRICT ON UPDATE CASCADE;
