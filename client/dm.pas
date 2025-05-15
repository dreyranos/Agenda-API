unit dm;

interface

uses
  System.SysUtils, System.Classes, FireDAC.Stan.Intf, FireDAC.Stan.Option,
  FireDAC.Stan.Error, FireDAC.UI.Intf, FireDAC.Phys.Intf, FireDAC.Stan.Def,
  FireDAC.Stan.Pool, FireDAC.Stan.Async, FireDAC.Phys, FireDAC.FMXUI.Wait,
  FireDAC.Stan.Param, FireDAC.DatS, FireDAC.DApt.Intf, FireDAC.DApt, Data.DB,
  FireDAC.Comp.DataSet, FireDAC.Comp.Client, System.IniFiles, FireDAC.VCLUI.Wait,
  FireDAC.Phys.FB, FireDAC.Phys.FBDef;

type
  TDataModule1 = class(TDataModule)
    database: TFDConnection;
    qryDias: TFDQuery;
    qryDiasDATA_EVENTO: TDateField;
    qryDiasQUANTIDADE_EVENTOS: TLargeintField;

  private
    { Private declarations }
  public
    { Public declarations }
  end;

var
  DataModule1: TDataModule1;

implementation


{%CLASSGROUP 'FMX.Controls.TControl'}
{$R *.dfm}



end.
