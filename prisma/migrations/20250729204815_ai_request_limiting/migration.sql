-- CreateTable
CREATE TABLE "AI_Request" (
    "id" SERIAL NOT NULL,
    "user_id" TEXT NOT NULL,
    "request_count" INTEGER NOT NULL DEFAULT 0,
    "last_request_at" TIMESTAMP(3) NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT "AI_Request_pkey" PRIMARY KEY ("id")
);

-- AddForeignKey
ALTER TABLE "AI_Request" ADD CONSTRAINT "AI_Request_user_id_fkey" FOREIGN KEY ("user_id") REFERENCES "User"("uid") ON DELETE RESTRICT ON UPDATE CASCADE;
