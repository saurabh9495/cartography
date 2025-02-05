from cartography.intel.aws import iam

SINGLE_STATEMENT = {
    "Resource": "*",
    "Action": "*",
}

# Example principal field in an AWS policy statement
# see: https://docs.aws.amazon.com/IAM/latest/UserGuide/reference_policies_elements_principal.html
SINGLE_PRINCIPAL = {
    "AWS": "test-role-1",
    "Service": ["test-service-1", "test-service-2"],
    "Federated": "test-provider-1",
}


def test__generate_policy_statements():
    statements = iam._transform_policy_statements(SINGLE_STATEMENT, "test_policy_id")
    assert isinstance(statements, list)
    assert isinstance(statements[0]["Action"], list)
    assert isinstance(statements[0]["Resource"], list)
    assert statements[0]["id"] == "test_policy_id/statement/1"


def test__parse_principal_entries():
    principal_entries = iam._parse_principal_entries(SINGLE_PRINCIPAL)
    assert isinstance(principal_entries, list)
    assert len(principal_entries) == 4
    assert principal_entries[0] == ("AWS", "test-role-1")
    assert principal_entries[1] == ("Service", "test-service-1")
    assert principal_entries[2] == ("Service", "test-service-2")
    assert principal_entries[3] == ("Federated", "test-provider-1")


def test_get_account_from_arn():
    result = iam.get_account_from_arn("arn:aws:iam::081157660428:role/TestRole")
    assert result == "081157660428"


def test__get_role_tags_valid_tags(mocker):
    mocker.patch(
        'cartography.intel.aws.iam.get_role_list_data', return_value=[
            {
                'RoleName': 'test-role',
                'Arn': 'test-arn',
            },
        ],
    )
    mocker.patch('boto3.session.Session')
    mock_session = mocker.Mock()
    mock_client = mocker.Mock()
    mock_role = mocker.Mock()
    mock_role.tags = [
        {
            'Key': 'k1', 'Value': 'v1',
        },
    ]
    mock_client.Role.return_value = mock_role
    mock_session.resource.return_value = mock_client
    result = iam.get_role_tags(mock_session)

    assert result == [{
        'ResourceARN': 'test-arn',
        'Tags': [
            {
                'Key': 'k1',
                'Value': 'v1',
            },
        ],
    }]


def test__get_role_tags_no_tags(mocker):
    mocker.patch(
        'cartography.intel.aws.iam.get_role_list_data', return_value=[
            {
                'RoleName': 'test-role',
                'Arn': 'test-arn',
            },
        ],
    )
    mocker.patch('boto3.session.Session')
    mock_session = mocker.Mock()
    mock_client = mocker.Mock()
    mock_role = mocker.Mock()
    mock_role.tags = [
    ]
    mock_client.Role.return_value = mock_role
    mock_session.resource.return_value = mock_client
    result = iam.get_role_tags(mock_session)

    assert result == []
