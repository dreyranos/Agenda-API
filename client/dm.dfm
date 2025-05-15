object DataModule1: TDataModule1
  Height = 480
  Width = 640
  object database: TFDConnection
    Params.Strings = (
      'Database=C:\AgendaBot\database\database.fdb'
      'User_Name=sysdba'
      'Password=masterkey'
      'DriverID=fB')
    Connected = True
    LoginPrompt = False
    Left = 48
    Top = 24
  end
  object qryDias: TFDQuery
    Connection = database
    SQL.Strings = (
      'SELECT'
      '    CAST(INICIO AS DATE) AS DATA_EVENTO,'
      '    COUNT(*) AS QUANTIDADE_EVENTOS'
      'FROM '
      '    AGENDA_EVENTOS'
      'WHERE '
      '    INICIO IS NOT NULL'
      '    AND LOWER(TITULO) NOT LIKE '#39'%anivers'#225'rio%'#39
      '    AND LOWER(TITULO) NOT LIKE '#39'%parab'#233'ns%'#39
      '    -- AND TIPO = '#39'EVENTO'#39'  -- Opcional: filtrar apenas eventos'
      'GROUP BY '
      '    CAST(INICIO AS DATE)'
      'ORDER BY '
      '    CASE '
      
        '        WHEN CAST(INICIO AS DATE) = CURRENT_DATE THEN 0  -- Dia ' +
        'atual primeiro'
      '        ELSE 1'
      '    END,'
      '    DATA_EVENTO DESC;  -- Depois ordena por data decrescente')
    Left = 48
    Top = 80
    object qryDiasDATA_EVENTO: TDateField
      AutoGenerateValue = arDefault
      FieldName = 'DATA_EVENTO'
      Origin = 'DATA_EVENTO'
      ProviderFlags = []
      ReadOnly = True
    end
    object qryDiasQUANTIDADE_EVENTOS: TLargeintField
      AutoGenerateValue = arDefault
      FieldName = 'QUANTIDADE_EVENTOS'
      Origin = 'QUANTIDADE_EVENTOS'
      ProviderFlags = []
      ReadOnly = True
    end
  end
end
