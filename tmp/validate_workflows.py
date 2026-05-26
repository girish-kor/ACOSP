import yaml
import json
import sys

workflow_files = [
    '.github/workflows/ci-cd.yml',
    '.github/workflows/deploy-manual.yml',
    '.github/workflows/release.yml',
    '.github/workflows/security.yml'
]

print("=" * 70)
print("GITHUB WORKFLOW VALIDATION TEST")
print("=" * 70)

# 1. YAML Syntax Check
print("\n[1] YAML SYNTAX VALIDATION\n")
yaml_errors = []
for file in workflow_files:
    try:
        with open(file, 'r') as f:
            workflow = yaml.safe_load(f)
        print(f"  ✓ {file}")
    except yaml.YAMLError as e:
        yaml_errors.append((file, str(e)))
        print(f"  ✗ {file}: {str(e)}")
    except FileNotFoundError:
        yaml_errors.append((file, "File not found"))
        print(f"  ✗ {file}: File not found")

if yaml_errors:
    print("\n❌ YAML validation FAILED")
else:
    print("\n✅ All YAML syntax is valid")

# 2. Workflow Structure Check
print("\n[2] WORKFLOW STRUCTURE VALIDATION\n")
structure_errors = []

for file in workflow_files:
    with open(file, 'r') as f:
        workflow = yaml.safe_load(f)
    
    # Check required top-level keys
    if 'name' not in workflow:
        structure_errors.append((file, "Missing 'name' field"))
    
    if 'on' not in workflow:
        structure_errors.append((file, "Missing 'on' (trigger) field"))
    
    if 'jobs' not in workflow:
        structure_errors.append((file, "Missing 'jobs' field"))
    
    # Check jobs have steps or use 'uses'
    if 'jobs' in workflow:
        for job_name, job_config in workflow['jobs'].items():
            if not isinstance(job_config, dict):
                structure_errors.append((file, f"Job '{job_name}' is not a dict"))
                continue
            
            # Check for either steps or uses (composite/reusable workflows)
            if 'steps' not in job_config and 'uses' not in job_config:
                # Some jobs might have only other properties
                if not any(k in job_config for k in ['runs-on', 'strategy', 'needs']):
                    structure_errors.append((file, f"Job '{job_name}' has no steps or uses"))

if structure_errors:
    print("⚠️  Structure issues found:")
    for file, error in structure_errors:
        print(f"  {file}: {error}")
else:
    print("  ✓ All workflows have correct structure")

# 3. Job Dependencies Check
print("\n[3] JOB DEPENDENCIES VALIDATION\n")
dep_errors = []

for file in workflow_files:
    with open(file, 'r') as f:
        workflow = yaml.safe_load(f)
    
    if 'jobs' in workflow:
        job_names = set(workflow['jobs'].keys())
        
        for job_name, job_config in workflow['jobs'].items():
            if isinstance(job_config, dict) and 'needs' in job_config:
                needs = job_config['needs']
                if isinstance(needs, str):
                    needs = [needs]
                
                for needed_job in needs:
                    if needed_job not in job_names:
                        dep_errors.append((file, f"Job '{job_name}' depends on non-existent job '{needed_job}'"))

if dep_errors:
    print("❌ Dependency errors found:")
    for file, error in dep_errors:
        print(f"  {file}: {error}")
else:
    print("  ✓ All job dependencies are valid")

# 4. Secret/Env Variable Check
print("\n[4] SECRETS & VARIABLES CHECK\n")
secrets_used = {}

for file in workflow_files:
    with open(file, 'r') as f:
        content = f.read()
    
    # Simple regex-like check for secrets
    import re
    secrets = re.findall(r'\$\{\{\s*secrets\.\w+\s*\}\}', content)
    if secrets:
        secrets_used[file] = list(set(secrets))

if secrets_used:
    print("  Secrets referenced in workflows:")
    for file, secret_list in secrets_used.items():
        print(f"  {file}:")
        for secret in secret_list:
            print(f"    - {secret}")
    print("\n  ⚠️  Ensure these secrets are configured in GitHub repository settings!")
else:
    print("  ℹ️  No secrets referenced (check if credentials are needed)")

# 5. Docker Configuration Check
print("\n[5] DOCKER CONFIGURATION CHECK\n")
docker_issues = []

try:
    with open('Dockerfile', 'r') as f:
        dockerfile_content = f.read()
    print("  ✓ Dockerfile exists")
    
    # Check for ENTRYPOINT or CMD
    if 'ENTRYPOINT' not in dockerfile_content and 'CMD' not in dockerfile_content:
        docker_issues.append("Dockerfile: Missing ENTRYPOINT or CMD")
    
    # Check for USER directive (security best practice)
    if 'USER' not in dockerfile_content:
        print("  ⚠️  Dockerfile: No USER directive (running as root)")
    else:
        print("  ✓ Dockerfile: USER directive found")
        
except FileNotFoundError:
    docker_issues.append("Dockerfile not found")

try:
    with open('docker-compose.yaml', 'r') as f:
        compose = yaml.safe_load(f)
    print("  ✓ docker-compose.yaml is valid YAML")
    
    if 'services' not in compose:
        docker_issues.append("docker-compose.yaml: Missing 'services' field")
    else:
        print(f"  ✓ docker-compose.yaml: {len(compose['services'])} services defined")
        
except yaml.YAMLError as e:
    docker_issues.append(f"docker-compose.yaml: {str(e)}")
except FileNotFoundError:
    docker_issues.append("docker-compose.yaml not found")

if docker_issues:
    print("\n❌ Docker configuration issues:")
    for issue in docker_issues:
        print(f"  {issue}")
else:
    print("  ✓ Docker configuration looks good")

# 6. pyproject.toml Check
print("\n[6] PYTHON CONFIGURATION CHECK\n")
python_issues = []

try:
    import tomllib
except ImportError:
    import toml as tomllib

try:
    with open('pyproject.toml', 'r') as f:
        if hasattr(tomllib, 'loads'):
            pyproject = tomllib.loads(f.read())
        else:
            pyproject = tomllib.load(f)
    
    if 'project' in pyproject and 'name' in pyproject['project']:
        print(f"  ✓ Project: {pyproject['project']['name']}")
    
    if 'project' in pyproject and 'version' in pyproject['project']:
        print(f"  ✓ Version: {pyproject['project']['version']}")
    
    if 'project' in pyproject and 'dependencies' in pyproject['project']:
        print(f"  ✓ {len(pyproject['project']['dependencies'])} dependencies defined")
        
except Exception as e:
    python_issues.append(f"pyproject.toml: {str(e)}")

if python_issues:
    print("\n❌ Python configuration issues:")
    for issue in python_issues:
        print(f"  {issue}")

# SUMMARY
print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)

total_issues = len(yaml_errors) + len(structure_errors) + len(dep_errors) + len(docker_issues) + len(python_issues)

if total_issues == 0:
    print("\n✅ ALL TESTS PASSED - Your workflows are correctly configured!")
    print("\nNext steps:")
    print("  1. Ensure GitHub secrets are configured (GITHUB_TOKEN, SLACK_WEBHOOK, PYPI_TOKEN, etc.)")
    print("  2. Test CI/CD pipeline by creating a pull request")
    print("  3. Verify Docker image builds successfully")
    print("  4. Monitor workflow runs in GitHub Actions")
else:
    print(f"\n❌ {total_issues} issue(s) found")
    print("\nSee details above for what needs to be fixed")

sys.exit(0 if total_issues == 0 else 1)
