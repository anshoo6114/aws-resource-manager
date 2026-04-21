# AWS Resource Manager

Comprehensive Python-based solution to manage AWS resources (EC2, RDS, ECR) and GitHub self-hosted runners via CLI or GitHub Actions.

## Features

✅ **EC2 Management**: Start/stop instances, check status
✅ **RDS Management**: Start/stop database instances  
✅ **ECR Management**: List repositories and images
✅ **GitHub Runners**: List and manage self-hosted runners
✅ **GitHub Actions Integration**: Workflow dispatch for automation
✅ **Comprehensive Logging**: Detailed operation tracking
✅ **Error Handling**: Robust error management and reporting
✅ **JSON Output**: Machine-readable results

## Prerequisites

- Python 3.8+
- AWS credentials configured (via IAM roles, env vars, or profiles)
- AWS IAM permissions for EC2, RDS, ECR operations
- GitHub Personal Access Token (for runner operations)

## Installation

### Local Setup

```bash
# Clone repository
git clone <repo-url>
cd aws-resource-manager

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Make CLI script executable
chmod +x aws_resource_manager.sh
```

### Configure AWS Credentials

```bash
# Option 1: AWS CLI configuration
aws configure

# Option 2: Environment variables
export AWS_ACCESS_KEY_ID=your_access_key
export AWS_SECRET_ACCESS_KEY=your_secret_key
export AWS_DEFAULT_REGION=us-east-1

# Option 3: GitHub Actions (use OIDC role)
# See setup instructions below
```

## Usage

### Command Line

```bash
# Start EC2 instance
python aws_resource_manager.py --resource ec2 --operation start --ids i-0123456789abcdef0

# Stop RDS database
python aws_resource_manager.py --resource rds --operation stop --ids mydb-instance

# List ECR repositories
python aws_resource_manager.py --resource ecr --operation list

# Check EC2 status
python aws_resource_manager.py --resource ec2 --operation status --ids i-0123456789abcdef0

# Get RDS status
python aws_resource_manager.py --resource rds --operation status --ids mydb-instance

# List GitHub runners
python aws_resource_manager.py --resource github --operation list \
  --github-token ghp_xxxxxxxxxxxx \
  --github-repo owner/repo

# Output as JSON
python aws_resource_manager.py --resource ec2 --operation start --ids i-123456 --json-output
```

### Using Shell Wrapper

```bash
./aws_resource_manager.sh --resource ec2 --operation start --ids i-0123456789abcdef0
./aws_resource_manager.sh --help
```

### GitHub Actions

1. **Set up IAM Role (Recommended)**
   ```
   - Create an IAM role with EC2, RDS, ECR permissions
   - Configure GitHub OIDC provider
   - Set AWS_ROLE_TO_ASSUME secret in repository
   ```

2. **Set up Secrets**
   ```
   - AWS_ROLE_TO_ASSUME: arn:aws:iam::ACCOUNT:role/ROLE-NAME
   - GITHUB_TOKEN: GitHub personal access token (auto-provided)
   ```

3. **Trigger Workflow**
   - Go to repository → Actions → AWS Resource Manager
   - Click "Run workflow"
   - Fill in parameters and execute

## Examples

### Example 1: Start Multiple EC2 Instances

```bash
python aws_resource_manager.py \
  --resource ec2 \
  --operation start \
  --region us-west-2 \
  --ids i-111111 i-222222 i-333333
```

### Example 2: Stop RDS and Check Status

```bash
# Stop database
python aws_resource_manager.py \
  --resource rds \
  --operation stop \
  --ids production-db \
  --json-output

# Check status
python aws_resource_manager.py \
  --resource rds \
  --operation status \
  --ids production-db
```

### Example 3: List ECR Images

```bash
# List all ECR repositories
python aws_resource_manager.py --resource ecr --operation list

# Get images in specific repository
python aws_resource_manager.py \
  --resource ecr \
  --operation status \
  --ids my-app-repo
```

### Example 4: GitHub Actions Workflow

Manually trigger via GitHub UI or use GitHub CLI:

```bash
gh workflow run aws-resource-manager.yml \
  -f resource=ec2 \
  -f operation=start \
  -f region=us-east-1 \
  -f resource_ids=i-123456
```

## Architecture

```
┌─────────────────────────────────────────┐
│   GitHub Actions / CLI                  │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  aws_resource_manager.py                │
│  - Argument Parsing                     │
│  - Resource Routing                     │
│  - Error Handling                       │
└──────────────┬──────────────────────────┘
               │
        ┌──────┴──────┬──────────┬────────┐
        ▼             ▼          ▼        ▼
   ┌────────┐   ┌────────┐  ┌─────┐  ┌──────────┐
   │ EC2    │   │ RDS    │  │ ECR │  │ GitHub   │
   │ Client │   │ Client │  │ Client│ API      │
   └────────┘   └────────┘  └─────┘  └──────────┘
        │             │         │        │
        ▼             ▼         ▼        ▼
   ┌─────────────────────────────────────────────┐
   │         AWS Services / GitHub API           │
   └─────────────────────────────────────────────┘
```

## Error Handling

The script handles various error scenarios:

- Invalid resource/operation combinations
- AWS credential failures
- Missing required parameters
- API rate limiting
- Network timeouts

All errors are logged with detailed messages for debugging.

## Logging

Logs are output to console with the following format:

```
YYYY-MM-DD HH:MM:SS - aws_resource_manager - INFO - <message>
```

## Security Best Practices

1. **Never commit AWS credentials** - Use IAM roles or environment variables
2. **Use GitHub OIDC** - Configure OIDC for GitHub Actions instead of long-lived credentials
3. **Rotate GitHub tokens** - Regularly rotate personal access tokens
4. **Principle of Least Privilege** - Grant minimal required IAM permissions
5. **Audit logs** - Monitor CloudTrail for resource management operations

## Required IAM Permissions

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "ec2:StartInstances",
        "ec2:StopInstances",
        "ec2:DescribeInstances"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "rds:StartDBInstance",
        "rds:StopDBInstance",
        "rds:DescribeDBInstances"
      ],
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "ecr:DescribeRepositories",
        "ecr:DescribeImages"
      ],
      "Resource": "*"
    }
  ]
}
```

## Troubleshooting

### Issue: "Unable to locate credentials"
- Configure AWS credentials using `aws configure`
- Or set environment variables: `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`

### Issue: "Access Denied" errors
- Verify IAM role has required permissions
- Check resource ARNs are correct
- Ensure user has permission to assume the role

### Issue: "Resource not found"
- Verify resource IDs are correct
- Check resource exists in the specified region
- Ensure you're using correct region with `--region`

### Issue: GitHub API errors
- Verify GitHub token has `repo` and `admin:repo_hook` scopes
- Check token is not expired
- Ensure repository path is `owner/repo` format

## Contributing

Contributions are welcome! Please:

1. Fork repository
2. Create feature branch
3. Add tests for new functionality
4. Submit pull request

## License

MIT License - See LICENSE file for details

## Support

For issues, questions, or suggestions:
- Open GitHub Issue
- Contact: [Your Contact]
- Documentation: [Link to docs]

---

**Last Updated**: 2024