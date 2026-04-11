from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

from app.services.planner_service import PlannerService
from app.services.generator_service import GeneratorService
from app.services.debug_service import DebugService
from app.services.tester_service import TesterService

logger = logging.getLogger(__name__)


class PipelineService:
    def __init__(self):
        self.planner_service = PlannerService()
        self.generator_service = GeneratorService()
        self.debug_service = DebugService()
        self.tester_service = TesterService()
        self.current_status = "idle"
        self.progress_logs = []
        
    def _add_log(self, message: str):
        self.progress_logs.append(message)
        self.current_status = message
        logger.info(f"PROGRESS: {message}")

    def get_progress(self):
        return {
            "status": self.current_status,
            "logs": self.progress_logs[-5:] # return last 5 logs
        }
    
    async def run_full_pipeline(
        self,
        user_prompt: str,
        components: Optional[List[str]] = None,
        auto_fix: bool = True,
        generate_tests: bool = True,
        validate_api: bool = False
    ) -> Dict[str, Any]:
        """
        Run the complete pipeline: User Prompt → Planner → Generator → Debug → Tester → Final Output.
        
        Args:
            user_prompt: User's project description
            components: Components to generate ['frontend', 'backend']
            auto_fix: Whether to automatically fix detected issues
            generate_tests: Whether to generate test cases
            validate_api: Whether to validate API endpoints
            
        Returns:
            Dictionary containing complete pipeline results
        """
        logger.info(f"Starting full pipeline for: {user_prompt[:100]}...")
        
        pipeline_start_time = datetime.now()
        
        self.current_status = "running"
        self.progress_logs = ["Pipeline started"]
        pipeline_result = {
            "user_prompt": user_prompt,
            "pipeline_status": "in_progress",
            "stages": {},
            "final_output": {},
            "errors": [],
            "warnings": [],
            "started_at": pipeline_start_time.isoformat()
        }
        
        try:
            # Stage 1: Planning
            self._add_log("Stage 1: Planning project structure...")
            stage_start = datetime.now()
            
            try:
                plan_result = await self.planner_service.create_project_plan(user_prompt)
                pipeline_result["stages"]["planning"] = {
                    "status": "completed",
                    "duration_seconds": (datetime.now() - stage_start).total_seconds(),
                    "result": plan_result
                }
                self._add_log("Planning completed successfully")
            except Exception as e:
                error_msg = f"Planning failed: {str(e)}"
                pipeline_result["errors"].append(error_msg)
                pipeline_result["stages"]["planning"] = {
                    "status": "failed",
                    "duration_seconds": (datetime.now() - stage_start).total_seconds(),
                    "error": error_msg
                }
                raise
            
            # Stage 2: Code Generation
            self._add_log("Stage 2: AI is writing the code files...")
            stage_start = datetime.now()
            
            try:
                plan = plan_result["plan"]
                self._add_log(f"Generating components for {plan.get('project_name', 'project')}...")
                generation_result = await self.generator_service.generate_code(
                    plan=plan,
                    components=components or ["frontend", "backend"]
                )
                pipeline_result["stages"]["generation"] = {
                    "status": "completed",
                    "duration_seconds": (datetime.now() - stage_start).total_seconds(),
                    "result": generation_result
                }
                self._add_log(f"Code generation completed: {generation_result.get('total_files', 0)} files")
            except Exception as e:
                error_msg = f"Code generation failed: {str(e)}"
                pipeline_result["errors"].append(error_msg)
                pipeline_result["stages"]["generation"] = {
                    "status": "failed",
                    "duration_seconds": (datetime.now() - stage_start).total_seconds(),
                    "error": error_msg
                }
                raise
            
            # Stage 3: Debugging
            logger.info("Stage 3: Debugging...")
            stage_start = datetime.now()
            
            try:
                generated_files = generation_result["files"]
                # Flatten all files from all components
                all_files = {}
                for component, files in generated_files.items():
                    all_files.update(files)
                
                if auto_fix:
                    debug_result = await self.debug_service.debug_and_fix(all_files)
                else:
                    debug_result = await self.debug_service.analyze_code(all_files)
                
                pipeline_result["stages"]["debugging"] = {
                    "status": "completed",
                    "duration_seconds": (datetime.now() - stage_start).total_seconds(),
                    "result": debug_result
                }
                
                # Use fixed files for next stage
                if auto_fix and "fix_result" in debug_result:
                    fixed_files = debug_result["fix_result"]["fixed_files"]
                    # Reorganize fixed files by component
                    pipeline_result["stages"]["debugging"]["fixed_files"] = fixed_files
                else:
                    fixed_files = all_files
                
                logger.info("Debugging completed successfully")
            except Exception as e:
                error_msg = f"Debugging failed: {str(e)}"
                pipeline_result["errors"].append(error_msg)
                pipeline_result["stages"]["debugging"] = {
                    "status": "failed",
                    "duration_seconds": (datetime.now() - stage_start).total_seconds(),
                    "error": error_msg
                }
                # Continue with original files if debugging fails
                fixed_files = all_files
            
            # Stage 4: Testing
            logger.info("Stage 4: Testing...")
            stage_start = datetime.now()
            
            testing_results = {}
            
            try:
                if generate_tests:
                    # Generate tests
                    test_generation_result = await self.tester_service.generate_tests(fixed_files)
                    testing_results["test_generation"] = test_generation_result
                    
                    # Run tests (mock implementation)
                    test_execution_result = await self.tester_service.run_tests(
                        test_generation_result["generated_tests"]
                    )
                    testing_results["test_execution"] = test_execution_result
                
                if validate_api:
                    # Validate API endpoints
                    api_validation_result = await self.tester_service.validate_api_endpoints()
                    testing_results["api_validation"] = api_validation_result
                
                pipeline_result["stages"]["testing"] = {
                    "status": "completed",
                    "duration_seconds": (datetime.now() - stage_start).total_seconds(),
                    "result": testing_results
                }
                logger.info("Testing completed successfully")
                
            except Exception as e:
                error_msg = f"Testing failed: {str(e)}"
                pipeline_result["errors"].append(error_msg)
                pipeline_result["warnings"].append("Testing stage failed, but pipeline continues")
                pipeline_result["stages"]["testing"] = {
                    "status": "failed",
                    "duration_seconds": (datetime.now() - stage_start).total_seconds(),
                    "error": error_msg
                }
            
            # Prepare final output
            pipeline_result["pipeline_status"] = "completed"
            
            # DEBUG: Log results
            files_count = len(fixed_files) if fixed_files else 0
            print(f"!!! CRITICAL DEBUG !!! Files generated in stage: {files_count}")
            logger.info(f"Pipeline Result: {files_count} files produced.")
            
            pipeline_result["final_output"] = {
                "project_plan": plan_result.get("plan", {}),
                "generated_code": fixed_files,
                "debug_results": debug_result,
                "test_results": testing_results,
                "summary": self._generate_pipeline_summary(pipeline_result)
            }
            
            # Save to disk for inspection
            try:
                with open("debug_pipeline_output.json", "w") as f:
                    import json
                    json.dump(pipeline_result["final_output"], f, indent=2)
            except:
                pass
            
        except Exception as e:
            pipeline_result["pipeline_status"] = "failed"
            pipeline_result["errors"].append(f"Pipeline failed: {str(e)}")
            logger.error(f"Pipeline failed: {str(e)}")
        
        finally:
            pipeline_result["completed_at"] = datetime.now().isoformat()
            pipeline_result["total_duration_seconds"] = (
                datetime.now() - pipeline_start_time
            ).total_seconds()
        
        return pipeline_result
    
    def _generate_pipeline_summary(self, pipeline_result: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the pipeline execution."""
        stages = pipeline_result.get("stages", {})
        
        summary = {
            "total_stages": len(stages),
            "completed_stages": len([s for s in stages.values() if s.get("status") == "completed"]),
            "failed_stages": len([s for s in stages.values() if s.get("status") == "failed"]),
            "total_errors": len(pipeline_result.get("errors", [])),
            "total_warnings": len(pipeline_result.get("warnings", []))
        }
        
        # Add specific counts from each stage
        if "planning" in stages and stages["planning"].get("status") == "completed":
            plan = stages["planning"]["result"].get("plan", {})
            summary["features_planned"] = len(plan.get("features", []))
            summary["tech_stack_items"] = sum(
                len(tech_list) for tech_list in plan.get("tech_stack", {}).values()
            )
        
        if "generation" in stages and stages["generation"].get("status") == "completed":
            summary["files_generated"] = stages["generation"]["result"].get("total_files", 0)
        
        if "debugging" in stages and stages["debugging"].get("status") == "completed":
            debug_result = stages["debugging"]["result"]
            if "analysis" in debug_result:
                summary["errors_found"] = debug_result["analysis"].get("total_errors", 0)
                summary["warnings_found"] = debug_result["analysis"].get("total_warnings", 0)
            if "fix_result" in debug_result:
                summary["fixes_applied"] = debug_result["fix_result"].get("total_fixes_applied", 0)
        
        if "testing" in stages and stages["testing"].get("status") == "completed":
            test_result = stages["testing"]["result"]
            if "test_execution" in test_result:
                summary["tests_run"] = test_result["test_execution"].get("total_tests_run", 0)
                summary["test_success_rate"] = test_result["test_execution"].get("success_rate", 0)
            if "api_validation" in test_result:
                summary["api_endpoints_tested"] = test_result["api_validation"].get("total_endpoints_tested", 0)
                summary["api_success_rate"] = test_result["api_validation"].get("success_rate", 0)
        
        return summary
    
    async def run_pipeline_step(
        self,
        step: str,
        input_data: Dict[str, Any],
        options: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Run a specific step in the pipeline.
        
        Args:
            step: The step to run ('planning', 'generation', 'debugging', 'testing')
            input_data: Input data for the step
            options: Additional options for the step
            
        Returns:
            Dictionary containing step results
        """
        logger.info(f"Running pipeline step: {step}")
        
        options = options or {}
        
        try:
            if step == "planning":
                return await self.planner_service.create_project_plan(
                    input_data.get("user_prompt", "")
                )
            
            elif step == "generation":
                return await self.generator_service.generate_code(
                    plan=input_data.get("plan", {}),
                    components=options.get("components", ["frontend", "backend"])
                )
            
            elif step == "debugging":
                files = input_data.get("files", {})
                if options.get("auto_fix", True):
                    return await self.debug_service.debug_and_fix(files)
                else:
                    return await self.debug_service.analyze_code(files)
            
            elif step == "testing":
                if options.get("generate_tests", True):
                    test_files = await self.tester_service.generate_tests(input_data.get("files", {}))
                    if options.get("run_tests", True):
                        test_results = await self.tester_service.run_tests(test_files["generated_tests"])
                        return {"test_generation": test_files, "test_execution": test_results}
                    return test_files
                
                if options.get("validate_api", False):
                    return await self.tester_service.validate_api_endpoints(
                        options.get("api_base_url", "http://localhost:8000")
                    )
            
            else:
                raise ValueError(f"Unknown pipeline step: {step}")
        
        except Exception as e:
            logger.error(f"Pipeline step '{step}' failed: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "step": step
            }
    
    def get_pipeline_status(self) -> Dict[str, Any]:
        """Get the status of all pipeline services."""
        return {
            "planner_service": {
                "configured": self.planner_service.is_configured(),
                "type": "planning"
            },
            "generator_service": {
                "configured": True,
                "supported_components": self.generator_service.get_supported_components(),
                "type": "generation"
            },
            "debug_service": {
                "configured": True,
                "supported_languages": self.debug_service.get_supported_languages(),
                "type": "debugging"
            },
            "tester_service": {
                "configured": True,
                "supported_languages": self.tester_service.get_supported_languages(),
                "type": "testing"
            }
        }
