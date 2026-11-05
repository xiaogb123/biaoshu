"""任务查询。

上传接口返回 job_id 之后，客户端靠这个接口轮询进度。

Day 3 只做「查」，不做取消 / 重试——那些等第 3 周有真实需求再说。
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.models import Job
from app.db.session import get_db
from app.schemas.document import JobOut

router = APIRouter(prefix = "/api/v1/jobs",tags=["jobs"])


@router.get("/{job_id}",response_model=JobOut)
def get_job(job_id:int,db:Session = Depends(get_db)) -> Job:
    job = db.get(Job, job_id)
    if job is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND,f"job {job_id} 不存在")
    return job